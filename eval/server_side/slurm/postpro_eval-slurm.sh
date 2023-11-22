#!/bin/bash

#SBATCH -N 1
#SBATCH -p queue1
#SBATCH -t 01:00:00
#SBATCH --ntasks-per-node=2

#SBATCH --array=1-10%150   # Adjust 1-100 to match the number of UUIDs in your file
#SBATCH --job-name=array_job
#SBATCH --output=logs/slurm-%A_%a.out
#SBATCH --error=logs/slurm-%A_%a.err

# set -e
set -u
source ~/miniconda3/etc/profile.d/conda.sh
conda activate voip-eval

mkdir -p logs
sudo mkdir -p /data
sudo chmod -R go+rwx /data
df -h /data

SPLIT='test'


BUCKET=$1
RAW_S3_PREFIX=$2
VER=$3
TODO_LIST=$4

if [ ! -f $TODO_LIST ];then
	echo "Error: ${TODO_LIST} not exist"
	exit 1
fi
# Calculate line number
line_num=$SLURM_ARRAY_TASK_ID
# Read run_id from file
file_id=$(sed -n "${line_num}p" "${TODO_LIST}")


PROFILE="default"

DATA_BASE='/data'
RAW_DIR=$DATA_BASE/raw
mkdir -p $RAW_DIR
if [[ -z "${VER-}" ]]; then
  echo "The VER (clean/noisy) to eval is not defined."
fi

SRC_PATTERN="src_${SPLIT}/src_${VER}"
SRC_EVAL_PATTERN="src_${SPLIT}/src_clean"  #always use clean for eval!
SPLIT_OG_FILE="s3://raw-src-files/src_${SPLIT}.zip"




# prefixes on s3 bucket
SPLITTED_UPLOAD_PREFIX="splitted-${SPLIT}-audio-${VER}"
RESULT_BUCKET_PREFIX="results-${SPLIT}-${VER}"



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

if [[ ! -d /home/ubuntu/data/results ]];then
	mkdir -p /home/ubuntu/data/results
fi

rm "${DATA_BASE}"/results
ln -sf /home/ubuntu/data/results "${DATA_BASE}"
SPLIT_DIR_PATTERN="relayed-splitted-${VER}"


# Download raw audio
if [[ -f "${RAW_DIR}/${file_id}.wav" ]];then
	echo "skipping download cuz exists"
else
	aws s3 cp --quiet --profile "${PROFILE}" s3://"${BUCKET}"/"${RAW_S3_PREFIX}"/"${file_id}.wav" $RAW_DIR
	echo "download raw done"
fi


# Split Audio
if [[ -d "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}" ]]; then
	echo "Skipping splitting"
#else
#	if [[ -f "${DATA_BASE}/results/eval_results_${VER}_${file_id}.csv" ]]; then
#        echo "Skipping eval cuz exists"
else
	# TODO: add download and unzip if already splitted
	/usr/bin/time -v python voip_eval/postpro_utils.py "${DATA_BASE}" "${SRC_PATTERN}" "${RAW_DIR}/${file_id}.wav" "${SPLIT_DIR_PATTERN}"
#fi
fi


# Eval
# always use clean-radix as ground truth!

if [[ -f "${DATA_BASE}/results/eval_results_${VER}_${file_id}.csv" ]]; then
	echo "Skipping eval cuz exists"
else
	/usr/bin/time -v python voip_eval/eval_utils.py "${DATA_BASE}" "${SPLIT_DIR_PATTERN}" "${SRC_EVAL_PATTERN}" "${VER}" "${file_id}"
fi

# Upload Splitted

zip -r "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}.zip" "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}"
aws s3 cp --quiet --profile "${PROFILE}" "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}.zip" \
	s3://"${BUCKET}"/"${SPLITTED_UPLOAD_PREFIX}/"

# Upload Eval Result

aws s3 cp --quiet --profile "${PROFILE}" "${DATA_BASE}/results/eval_results_${VER}_${file_id}.csv" s3://"${BUCKET}"/"${RESULT_BUCKET_PREFIX}"/

## Remove splitted dir/eval result ...

rm "${RAW_DIR}/${file_id}.wav"
rm -r "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}"
rm "${DATA_BASE}/${SPLIT_DIR_PATTERN}/${file_id}.zip"


