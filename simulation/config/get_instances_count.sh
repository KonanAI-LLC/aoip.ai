#!/bin/bash

regions=(
    "us-east-1"
    "us-east-2"
    "us-west-1"
    "us-west-2"
    "af-south-1"
    "ap-east-1"
    "ap-south-1"
    "ap-southeast-1"
    "ap-southeast-2"
    "ap-northeast-1"
    "ap-northeast-2"
    "ca-central-1"
    "eu-central-1"
    "eu-west-1"
    "eu-west-2"
    "eu-west-3"
    "eu-south-1"
    "eu-north-1"
    "me-south-1"
    "sa-east-1"
)

for region in "${regions[@]}"; do
#    echo "Processing region: $region"
    
    # Get the number of running instances in the region
    instance_count=$(aws ec2 describe-instances --region "$region" --query "Reservations[*].Instances[?State.Name=='running']" --output text | wc -l)
    
    echo "Number of running instances in region $region: $instance_count"
done

