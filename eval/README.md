# AOIP Evaluation

# Setup AWS Parallel Cluster (from your local machine)
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
2. 

