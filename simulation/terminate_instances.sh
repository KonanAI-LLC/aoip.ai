#!/bin/bash

regions=($(aws ec2 describe-regions --query 'Regions[].RegionName' --output text))

for region in "${regions[@]}"; do
    (
        echo "Processing region: $region"

        # Terminate Instances
        instance_ids=$(aws ec2 describe-instances --region "$region" --query 'Reservations[*].Instances[*].[InstanceId]' --output text)
        if [ "$instance_ids" != "None" ] && [ ! -z "$instance_ids" ]; then
            aws ec2 terminate-instances --region "$region" --instance-ids $instance_ids
        else
            echo "No instances to terminate in region $region"
        fi

        # Delete Security Groups
        security_groups=$(aws ec2 describe-security-groups --region "$region" \
        --filters Name=group-name,Values='sg_simulation_*' \
        --query 'SecurityGroups[*].[GroupId]' --output text)

        if [ ! -z "$security_groups" ] && [ "$security_groups" != "None" ]; then
            for sg in $security_groups; do
                aws ec2 delete-security-group --region "$region" --group-id "$sg"
            done
        else
            echo "No security groups to delete in region $region matching the pattern sg_simulation_*"
        fi

        # Delete Key Pairs
        key_pairs=$(aws ec2 describe-key-pairs --region "$region" --query 'KeyPairs[*].[KeyName]' --output text)
        if [ ! -z "$key_pairs" ]; then
            for key in $key_pairs; do
                aws ec2 delete-key-pair --region "$region" --key-name "$key"
            done
        else
            echo "No key pairs to delete in region $region"
        fi
    ) &
done

