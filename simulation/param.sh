#!/bin/bash

counter=0
total_jobs=365 # Number of jobs to run in total

while IFS= read -r cmd || [ -n "$cmd" ]; do # read commands.txt line by line
    ((counter++))

    if [[ $counter -gt $total_jobs ]]; then
        break # Exit the loop after starting total_jobs jobs
    fi

    echo "Starting job $counter"

    eval "$cmd" & # run jobs in background

    sleep 5 # 2 second delay between starting each job
done <commands.txt

wait # Wait for all background jobs to complete
