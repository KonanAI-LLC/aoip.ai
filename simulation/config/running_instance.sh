#!/bin/bash

# Get an array of AWS regions
regions=($(aws ec2 describe-regions --query 'Regions[].RegionName' --output text))

# Loop over each region to get the count of active instances
for region in "${regions[@]}"; do
    # Query the EC2 instances in the specified region
    output=$(aws ec2 describe-instances --filters Name=instance-state-name,Values=running --query 'Reservations[*].Instances[*].InstanceId' --region "$region")
    
    # Count the number of active instances
    instance_count=$(echo $output | jq '. | flatten | length')
    
    echo "Region: $region, Active Instances: $instance_count"
done

