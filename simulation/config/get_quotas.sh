#!/bin/bash

# Get an array of AWS regions
regions=($(aws ec2 describe-regions --query 'Regions[].RegionName' --output text))

# Service and quota codes
service_code="ec2"
quota_code="L-1216C47A"

# Loop over each region and execute the command
for region in "${regions[@]}"; do
    output=$(aws service-quotas get-service-quota --service-code "$service_code" --quota-code "$quota_code" --region "$region")
    value=$(echo $output | jq -r '.Quota.Value')
    echo "Region: $region, Value: $value"
done
