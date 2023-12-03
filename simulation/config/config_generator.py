ami_ids = [
    ["ami-0f2b6f057e0b94d5f", "us-east-1", "t2.micro"],
    ["ami-0fc034eec6ebb0a2f", "us-east-2", "t2.micro"],
    ["ami-0dd46a9bd78933b59", "us-west-1", "t2.micro"],
    ["ami-0b0b696130ccae67a", "us-west-2", "t2.micro"],
    ["ami-06c953f35606c6cab", "af-south-1", "t3.micro"],
    ["ami-0b7f75070a9af5ccc", "ap-east-1", "t3.micro"],
    ["ami-039a3748ec7d927ea", "ap-south-1", "t2.micro"],
    ["ami-0cd432cfa44d54635", "ap-south-2", "t3.micro"],
    ["ami-048cf2b6094a8ddea", "ap-southeast-1", "t2.micro"],
    ["ami-08e2b80da2d1a26ba", "ap-southeast-2", "t2.micro"],
    ["ami-07cbd8baed4031a0b", "ap-southeast-3", "t3.micro"],
    ["ami-0b2d79b35cb407633", "ap-southeast-4", "t3.micro"],
    ["ami-03ede0e542255afab", "ap-northeast-1", "t2.micro"],
    ["ami-0194a3a85274df403", "ap-northeast-2", "t2.micro"],
    ["ami-0e3e14659906088ee", "ap-northeast-3", "t2.micro"],
    ["ami-061a9d1cbe679774f", "ca-central-1", "t2.micro"],
    ["ami-0503973bb9fd5bf9d", "eu-central-1", "t2.micro"],
    ["ami-08a393a6f1ae935ae", "eu-central-2", "t3.micro"],
    ["ami-06f9d95eb36b09c6d", "eu-west-1", "t2.micro"],
    ["ami-0289906f3a1cc9f6e", "eu-west-2", "t2.micro"],
    ["ami-033fffd5768abc474", "eu-west-3", "t2.micro"],
    ["ami-0f0fa2dc7875970ae", "eu-south-1", "t3.micro"],
    ["ami-01068005c34dbbeaa", "eu-south-2", "t3.micro"],
    ["ami-083e5cd2c4794ba06", "eu-north-1", "t3.micro"],
    ["ami-00d907c0f0dd4cea8", "me-south-1", "t3.micro"],
    ["ami-0bc3f735ec926ac10", "il-central-1", "t3.micro"],
    ["ami-0dbe45934592daa1d", "sa-east-1", "t2.micro"]
]

# with open("run_configs.txt", "w") as run_config:
#
#     for sender_ami, sender_region, sender_instance_type in ami_ids:
#         for receiver_ami, receiver_region, receive_instance_type in ami_ids:
#
#             # if sender_region == receiver_region:
#             #     continue
#             command = f"export PYTHONPATH=$PYTHONPATH:/home/shikhar/capstone/simulation " \
#                       f"&&  python utils/simulate_ami.py --sreg {sender_region} --rreg {receiver_region} --sins {sender_instance_type} --rins {receive_instance_type} --sami {sender_ami} --rami {receiver_ami} --src test_src_noisy --dur 1655 --subw 100 --sdbw 100 --rubw 100 --rdbw 100 --s3 s3://raw-src-files/src_noisy_test_4/"
#             # print(command)
#             run_config.write(command + "\n")

with open("run_configs.txt", "w") as run_config:

    for sender_ami, sender_region, sender_instance_type in ami_ids:
        # if sender_region == receiver_region:
        #     continue
        command = f"export PYTHONPATH=$PYTHONPATH:/Users/shikharagnihotri/Desktop/work/CAPSTONE/simulation " \
                  f"&&  python utils/simulate_ami.py --sreg {sender_region} --rreg {sender_region} --sins {sender_instance_type} --rins {sender_instance_type} --sami {sender_ami} --rami {sender_ami} --src test_src_noisy --dur 1655 --subw 100 --sdbw 100 --rubw 100 --rdbw 100 --s3 s3://raw-src-files/src_noisy_test_4/"
        # print(command)
        run_config.write(command + "\n")

# # aws ec2 terminate-instances --region ap-east-1 --instance-ids $(aws ec2 describe-instances --region ap-east-1 --query 'Reservations[*].Instances[*].[InstanceId]' --output text)
# "export PYTHONPATH=$PYTHONPATH:/home/shikhar/capstone/simulation &&  python utils/simulate.py --sreg ap-northeast-2 --rreg ap-northeast-3 --sins t2.micro --rins t2.micro --sami ami-0c9c942bd7bf113a2 --rami ami-0da13880f921c96a5 --src test_src_noisy --dur 16 --subw 100 --sdbw 100 --rubw 100 --rdbw 100 --s3 s3://raw-src-files/src_noisy_test/"