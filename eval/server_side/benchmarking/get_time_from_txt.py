import numpy as np

def time_string_to_minutes(time_string):
    minutes, seconds = map(float, time_string.replace('real\t', '').replace('s', '').split('m'))
    return minutes + seconds / 60

def calculate_summary_statistics(file_path):
    with open(file_path, 'r') as f:
        time_strings = f.readlines()
    
    time_values = [time_string_to_minutes(time_string.strip()) for time_string in time_strings]
    
    print("Summary Statistics (in minutes):")
    print("Count:",len(time_values))
    print("Mean:", np.mean(time_values))
    print("Median:", np.median(time_values))
    print("Minimum:", np.min(time_values))
    print("Maximum:", np.max(time_values))
    print("Standard Deviation:", np.std(time_values))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python script.py time_strings.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    calculate_summary_statistics(file_path)

