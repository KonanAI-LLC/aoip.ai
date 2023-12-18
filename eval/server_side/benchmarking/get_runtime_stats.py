import os
import re
import pandas as pd

def extract_time_info(text):
    time_info = re.findall(r'real\s*(.*)\nuser\s*(.*)\nsys\s*(.*)', text)
    return time_info

def convert_to_seconds(time_string):
    minutes, seconds = map(float, time_string.strip('s').split('m'))
    return 60 * minutes + seconds

def convert_seconds_to_minutes(seconds):
    return seconds / 60

def main(log_folder,job_id):
    blockA_data = {}
    blockB_data = {}

    for file in os.listdir(log_folder):
        if  file.startswith(f"slurm-{job_id}_") and file.endswith(".err"):
            job_id = file.split('_')[1].split('.')[0]
            with open(os.path.join(log_folder, file), 'r') as f:
                blockA_content = []
                blockB_content = []
                is_blockB = False
                for line in f:
                    if '/home/ubuntu/miniconda3/envs/voip-eval/lib/python3.10/site-packages/pysepm/' in line:
                        is_blockB = True
                    elif is_blockB:
                        blockB_content.append(line)
                    else:
                        blockA_content.append(line)
                
                blockA_time = extract_time_info(''.join(blockA_content))
                blockB_time = extract_time_info(''.join(blockB_content))
                if blockA_time:
                    blockA_data[job_id] = blockA_time[0]
                if blockB_time:
                    blockB_data[job_id] = blockB_time[-1]
    
    blockA_df = pd.DataFrame.from_dict(blockA_data, orient='index', columns=['Real', 'User', 'Sys'])
    blockB_df = pd.DataFrame.from_dict(blockB_data, orient='index', columns=['Real', 'User', 'Sys'])

    # Convert time strings to seconds for numerical calculations
    for col in ['Real', 'User', 'Sys']:
        blockA_df[col] = blockA_df[col].apply(convert_to_seconds)
        blockB_df[col] = blockB_df[col].apply(convert_to_seconds)

    print("Block A Data:")
    print(blockA_df)
    print("\nBlock B Data:")
    print(blockB_df)

    # Convert seconds to minutes for summary statistics
    blockA_stats_minutes = blockA_df.applymap(convert_seconds_to_minutes).describe()
    blockB_stats_minutes = blockB_df.applymap(convert_seconds_to_minutes).describe()

    print("\nSummary Statistics for Block A (in minutes):")
    print(blockA_stats_minutes)

    print("\nSummary Statistics for Block B (in minutes):")
    print(blockB_stats_minutes)

if __name__ == "__main__":
    import sys
    assert len(sys.argv)==2
    log_folder = 'logs'
    job_id=sys.argv[1]
    main(log_folder,job_id)

