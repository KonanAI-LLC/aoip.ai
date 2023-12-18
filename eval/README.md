# AOIP Evaluation

# Setup AWS Parallel Cluster (on your local machine)
1. install cli
```
pip install aws-parallelcluster
```

2. Install Node
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
chmod ug+x ~/.nvm/nvm.sh
source ~/.nvm/nvm.sh
nvm --help
nvm install --lts
node --version
```
3. Configure
setup your own config by doing
```
pcluster configure -c ~/.parallelcluster/config
```

We tested the code with the following setup

```
AWS Region ID [us-east-1]: [pick a region]
EC2 Key Pair Name: [your key]
Scheduler [slurm]: (default)
Operating System [alinux2]:3 (ubuntu2004)
Head node instance type [t2.micro]:t2.large
Number of queues [1]:1 //you can use this to have different mixture of instance types
Name of queue 1 [queue1]:
Number of compute resources for queue1 [1]:1 // you can use this to specify how many kinds of instance type are available
Compute instance type for compute resource 1 in queue1 [t2.micro]: t2.medium
Maximum instance count [10]: 149
Automate VPC creation? (y/n) [n]:y
Availability Zone [us-east-2a]: (default)
Network Configuration [Head node in a public subnet and compute fleet in a private subnet]: 2 (default has additional charges, we chose everything in public subnet)
```

# Cluster Environment Setup
1. Download the server_side code on the cluster head node
2. Run `./cluster-setup-env.sh`. Optionally run `./enh_setup.sh` to setup the environment for the enhancement model.
    * test your installation by running `python -m voip_eval.MultipleEvaluation` under the `server_side` directory

# Run Evaluation
1. Setup AWS profile on the cluster head node using `aws configure`
2. submit slurm job scripts
    1. prepare all file ids from s3 bucket in a txt file. split if too long using `./split_txt.sh [txt_file] [chunk_size]`
    2. This script implements a simple sleeping mechanism to submit array jobs to slurm queue in order not to crash the slurm scheduler.
    ```
        ./submit_jobs.sh JOB_ARRAY_SCRIPT TODO_PREFIX [SCRIPT_ARGS]
        1. JOB_ARRAY_SCRIPT: the script to run on each file id
        2. TODO_PREFIX: the prefix of the txt file containing all file ids (because we split one into multiple files)
        3. SCRIPT_ARGS: the arguments to pass to the script
    ```
3. Choices of script includes for relative evaluation metrics.
    1. `postpro_eval-slurm.sh`: run post-processing and  evaluation
    2. `eval-only-slurm.sh`: run evaluation only
    3. `slurm-enhan_eval.sh`: run enhancement and evaluation (cpu only)
    4. `gpu-slurm-enhan_eval.sh`: run enhancement and evaluation (gpu)

    These scripts produces a results csv file for each file_id. To get a summary results, you can run `python print_results.py --dataprefix [path/to/results/csv/files] --eval_pattern [eval_pattern]` where `eval_pattern` is a piece of string in the csv filename indicating the version of audio this is (e.g. clean/noisy/clean-enhan/noisy-enhan...) that you defined when you run the job scripts.

    The splitting and evaluation codes uses scripts inside `voip_eval/` directory. You can modify the scripts to change the evaluation metrics. The default is to use `pesq` and `stoi` for speech quality evaluation. You should run these scripts from the `server_side` directory. If you move your slurm scripts elsewhere, make sure to update the script paths accordingly.

    


