#!/bin/bash

# Check if sufficient arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 [txt_file] [chunk_size]"
    exit 1
fi

# Assigning arguments to variables
FILE=$1
CHUNK_SIZE=$2

# Check if file exists
if [ ! -f "$FILE" ]; then
    echo "File not found!"
    exit 1
fi

# Extract filename without extension
BASENAME=$(basename "$FILE" .txt)

# Split the file
split -l $CHUNK_SIZE --additional-suffix=.txt "$FILE" "${BASENAME}_"

# Rename the split files
COUNT=1
for f in ${BASENAME}_*; do
    mv "$f" "${BASENAME}_${COUNT}.txt"
    let COUNT++
done

echo "Splitting complete."

