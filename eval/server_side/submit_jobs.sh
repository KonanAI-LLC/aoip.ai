#!/bin/bash
SBATCH_OPTIONS_STR="-p queue2 -a 1-1000%149 --ntasks-per-node=1 --cpus-per-task=2"

echo "default to SBATCH_OPTIONS_STR=\"${SBATCH_OPTIONS_STR}\""

# Check if the job array script is provided
if [[ -z $1 ]]; then
    echo "Error: No job array script specified."
    echo "Usage: $0 JOB_ARRAY_SCRIPT TODO_PREFIX [SCRIPT_ARGS]"
    exit 1
fi

# Set the job array script
JOB_ARRAY_SCRIPT="$1"

# Check if the total number of arguments is less than 5
if [ $# -lt 5 ]; then
    echo "Insufficient arguments provided."
    # Run the job array script to display its usage message
    echo "Usage: $0 JOB_ARRAY_SCRIPT TODO_PREFIX [SCRIPT_ARGS]"
    echo "TODO_LIST=\${TODO_PREFIX}_\${i}.txt"
    ./${JOB_ARRAY_SCRIPT}
    exit 1
fi


# Configuration
JOB_ARRAY_SCRIPT="$1"  # First argument is the job array script name
YOUR_PREFIX="$2"       # Second argument is the prefix
MAX_JOBS=4             # Maximum number of jobs in the queue
SLEEP_TIME=600         # Time to sleep between checks (10 minutes)


# Function to get the current number of array jobs in the queue
get_job_count() {
    squeue | grep "\[" | wc -l
}

# Additional arguments to pass to the sbatch script (excluding the first two)
ADDITIONAL_ARGS="${@:3}"

# Initial index
i=1

# Main loop
while true; do
    # Check the current number of jobs
    job_count=$(get_job_count)
    
    while [[ $job_count -lt $MAX_JOBS ]]; do
        # Construct the file name
        file_name="${YOUR_PREFIX}_${i}.txt"
        
        # Check if the file exists
        if [[ -f "$file_name" ]]; then
            # Submit the job with additional arguments and increment the index
            # Construct the sbatch command as a string
            sbatch_command="sbatch ${SBATCH_OPTIONS_STR} ${JOB_ARRAY_SCRIPT} ${file_name} ${ADDITIONAL_ARGS}"
            
            # Echo the command for logging or debugging
            echo "Executing command: $sbatch_command"

            # Execute the sbatch command
            eval $sbatch_command

            let i++
        else
            echo "No more files to submit. Exiting."
            exit 0
        fi

        # Update the job count
        job_count=$(get_job_count)
    done

    # Wait for a while before checking again
    sleep $SLEEP_TIME
done
