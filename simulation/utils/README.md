## Running a Simulation 

## --help

```commandline
simulation/utils/simulate.py --help 
usage: simulate.py [-h] [--tracking_id TRACKING_ID] --sender_region
                   {us-east-1,us-west-1,eu-west-2,ap-south-1,ap-southeast-2}
                   --receiver_region
                   {us-east-1,us-west-1,eu-west-2,ap-south-1,ap-southeast-2}
                   [--sender_instance_type {t2.micro}]
                   [--receiver_instance_type {t2.micro}]
                   [--sender_instance_ami {ami-053b0d53c279acc90}]
                   [--receiver_instance_ami {ami-053b0d53c279acc90,ami-0310483fb2b488153}]
                   [--sender_upload_bandwidth SENDER_UPLOAD_BANDWIDTH]
                   [--sender_download_bandwidth SENDER_DOWNLOAD_BANDWIDTH]
                   [--receiver_upload_bandwidth RECEIVER_UPLOAD_BANDWIDTH]
                   [--receiver_download_bandwidth RECEIVER_DOWNLOAD_BANDWIDTH]
                   --src_audio_config
                   {test_src_noisy,test_src_clean,train_src_noisy,train_src_clean}
                   --duration DURATION --s3_bucket_url S3_BUCKET_URL

This script helps you to perform an e2e data collection run.

optional arguments:
  -h, --help            show this help message and exit
  --tracking_id TRACKING_ID, --id TRACKING_ID
                        An id to track your simulation
  --sender_region {us-east-1,us-west-1,eu-west-2,ap-south-1,ap-southeast-2}, --sreg {us-east-1,us-west-1,eu-west-2,ap-south-1,ap-southeast-2}
                        Sender region
  --receiver_region {us-east-1,us-west-1,eu-west-2,ap-south-1,ap-southeast-2}, --rreg {us-east-1,us-west-1,eu-west-2,ap-south-1,ap-southeast-2}
                        Receiver region
  --sender_instance_type {t2.micro}, --sins {t2.micro}
                        Sender instance type
  --receiver_instance_type {t2.micro}, --rins {t2.micro}
                        Receiver instance type
  --sender_instance_ami {ami-053b0d53c279acc90}, --sami {ami-053b0d53c279acc90}
                        Sender instance ami id
  --receiver_instance_ami {ami-053b0d53c279acc90,ami-0310483fb2b488153}, --rami {ami-053b0d53c279acc90,ami-0310483fb2b488153}
                        Receiver instance ami id
  --sender_upload_bandwidth SENDER_UPLOAD_BANDWIDTH, --subw SENDER_UPLOAD_BANDWIDTH
                        Sender upload bandwidth
  --sender_download_bandwidth SENDER_DOWNLOAD_BANDWIDTH, --sdbw SENDER_DOWNLOAD_BANDWIDTH
                        Sender download bandwidth
  --receiver_upload_bandwidth RECEIVER_UPLOAD_BANDWIDTH, --rubw RECEIVER_UPLOAD_BANDWIDTH
                        Receiver upload bandwidth
  --receiver_download_bandwidth RECEIVER_DOWNLOAD_BANDWIDTH, --rdbw RECEIVER_DOWNLOAD_BANDWIDTH
                        Receiver download bandwidth
  --src_audio_config {test_src_noisy,test_src_clean,train_src_noisy,train_src_clean}, --src {test_src_noisy,test_src_clean,train_src_noisy,train_src_clean}
                        Source audio configuration
  --duration DURATION, --dur DURATION
                        Duration of call
  --s3_bucket_url S3_BUCKET_URL, --s3 S3_BUCKET_URL
                        S3 storage url

```

### Running a simulation

```commandline
python utils/simulate.py \
--sreg us-east-1 --rreg ap-southeast-2 --sins t2.micro --rins t2.micro --sami ami-053b0d53c279acc90 --rami ami-0310483fb2b488153 --src test_src_clean --dur 60 --subw 100 --sdbw 100 --rubw 100 --rdbw 100 --s3 s3://raw-src-files/recordings/
```
