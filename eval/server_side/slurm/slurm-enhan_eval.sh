#!/bin/bash

#SBATCH -N 1
#SBATCH -p queue1
#SBATCH -t 01:00:00
#SBATCH --ntasks-per-node=2

#SBATCH --array=1-10%150   # Adjust 1-100 to match the number of UUIDs in your file
#SBATCH --job-name=array_job
#SBATCH --output=logs-enh/slurm-%A_%a.out
#SBATCH --error=logs-enh/slurm-%A_%a.err

# set -e
set -u
source ~/miniconda3/etc/profile.d/conda.sh
conda activate voip-eval
echo "Using environment $(conda env export | grep name)"
conda deactivate

mkdir -p logs-enh
sudo mkdir -p /data
sudo chmod -R go+rwx /data
df -h /data

SPLIT='test'

BUCKET="ssh-new-test"
RAW_S3_PREFIX="ssh-nov-1"

DATA_BASE='/data'
RAW_DIR=$DATA_BASE/raw
mkdir -p $RAW_DIR

###### Validate Arguments ######
VER=$1 # this is the version of relayed audio we are enhancing (clean/noisy)
if [[ -z "${VER-}" ]]; then
  echo "The VER (clean/noisy) to eval is not defined."
  exit 1
fi
TODO_LIST=$2
if [ ! -f $2 ];then
	echo "Error: pending.txt not exist"
	exit 1
fi
#################################

SRC_PATTERN="src_${SPLIT}/src_${VER}"
SRC_EVAL_PATTERN="src_${SPLIT}/src_clean"  #always use clean for eval!
SPLIT_OG_FILE="s3://raw-src-files/src_${SPLIT}.zip"
PROFILE="default"


# prefixes on s3 bucket
SPLITTED_DOWNLOAD_PREFIX="splitted-${SPLIT}-audio-${VER}"




######### Download Groundtruth data ##########
exec 200>"${DATA_BASE}/.lock"
if flock -n 200;then
  if [[ ! -d "${DATA_BASE}/${SRC_PATTERN}" ]];then
	#cp -r /home/ubuntu/data/test150-og "${DATA_BASE}"
	aws s3 cp --profile "${PROFILE}" --quiet "${SPLIT_OG_FILE}" "${DATA_BASE}"/
	echo "download gt done"
	unzip "${DATA_BASE}/src_${SPLIT}.zip" -d ${DATA_BASE}/
	rm "${DATA_BASE}/src_${SPLIT}.zip"
  fi
  flock -u 200
else
  while [[ ! -d "${DATA_BASE}/${SRC_PATTERN}"  ]]; do
    echo "Waiting for ground truth..."
    sleep 5  # wait for 5 seconds before checking again
  done
fi
##############################################
if [[ ! -d /home/ubuntu/data/results ]];then
	mkdir -p /home/ubuntu/data/results
fi

rm -f "${DATA_BASE}"/results
ln -sf /home/ubuntu/data/results "${DATA_BASE}"
SPLIT_DIR_PATTERN="relayed-splitted-${VER}"
mkdir -p "${DATA_BASE}/${SPLIT_DIR_PATTERN}"

# Calculate line number
line_num=$SLURM_ARRAY_TASK_ID
# Read run_id from file
file_id=$(sed -n "${line_num}p" "${TODO_LIST}")

# Download Splitted Audio and unzip
aws s3 cp --profile "${PROFILE}" \
--quiet s3://"${BUCKET}"/"${SPLITTED_DOWNLOAD_PREFIX}/${file_id}.zip" \
"${DATA_BASE}/"
mkdir -p "${DATA_BASE}/temp"
unzip "${DATA_BASE}/${file_id}.zip" -d "${DATA_BASE}/temp"
rm "${DATA_BASE}/${file_id}.zip"
find "${DATA_BASE}/temp" -name ${file_id} -exec mv -t "${DATA_BASE}/${SPLIT_DIR_PATTERN}/" {} +

# ENHANCE
ENH_VER=enh-demucs # a piece of string to distinguish result files for clean/noisy/enhanced
ENH_ENV="enh"
ENH_OUT_DIR_PATTERN="enhed_${VER}_${ENH_VER}"
NUM_WORKERS=$(lscpu | grep ^CPU\(s\) | sed -n 's/CPU(s):\s*//p')
ENH_UPLOAD_PREFIX="splitted-${SPLIT}-audio-${VER}-${ENH_VER}"
RESULT_BUCKET_PREFIX="results-${SPLIT}-${ENH_VER}"
mkdir -p "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}"

conda activate "${ENH_ENV}"
cd ~/TAPLoss/Demucs/denoiser/
NOISY_FILENAMES="${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/noisy_${file_id}_filenames.json"
python -m denoiser.audio "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}" > $NOISY_FILENAMES

/usr/bin/time -v python -m denoiser.enhance --dns64 --num_workers "${NUM_WORKERS}" \
--noisy_json $NOISY_FILENAMES --out_dir "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}"
rm $NOISY_FILENAMES

# IMPORTANT: wildcard should not be in quotes!
rm -rf "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}/"*_noisy.wav
find "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}" -type f -name '*_enhanced.wav' | sed 'p;s/_enhanced.wav$/.wav/' | xargs -n2 mv
conda deactivate

######## UPLOAD ENH AUDIO ##############
zip -r "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}.zip" "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}"
aws s3 cp --quiet --profile "${PROFILE}" "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}.zip" \
	s3://"${BUCKET}"/"${ENH_UPLOAD_PREFIX}/"
rm "${DATA_BASE}/${ENH_OUT_DIR_PATTERN}/${file_id}.zip"

################# Eval #################
EVAL_ENV="voip-eval"

# always use clean-radix as ground truth!
cd ~/voip-eval
conda activate "${EVAL_ENV}"
if [[ -f "${DATA_BASE}/results/eval_results_${VER}_${file_id}.csv" ]]; then
	echo "Skipping eval cuz exists"
else
	/usr/bin/time -v python voip_eval/eval_utils.py "${DATA_BASE}" "${ENH_OUT_DIR_PATTERN}" "${SRC_EVAL_PATTERN}" "${ENH_VER}" "${file_id}"
fi
conda deactivate


# Upload Eval Result

aws s3 cp --quiet --profile "${PROFILE}" "${DATA_BASE}/results/eval_results_${ENH_VER}_${file_id}.csv" s3://"${BUCKET}"/"${RESULT_BUCKET_PREFIX}"/

## Remove splitted dir/eval result ...

rm -r "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}"


