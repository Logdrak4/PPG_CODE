#!/bin/bash

#define python scripts
PPG_SCRIPT="python_ppg.py"
ID_ALGORITHM="olaolu_algorithm.py"
OLED_SCRIPT="I2C_SCRIPT"

# IF video filepath is input
if [ "$#" -ne 1 ]; then
        echo "Usage: $0 <video_filepath>"
            exit 1
            fi

VIDEO_FILE=$1

echo "Booting System..."

echo "Running $PPG_SCRIPT..."
# Create a temporary file to capture the full output
TEMP_OUTPUT_FILE=$(mktemp)

# Run PPG extraction script and capture all output into the temporary file

python "$PPG_SCRIPT" "$VIDEO_FILE" > "$TEMP_OUTPUT_FILE" 2>&1

# Check if the Python script ran successfully
if [ $? -ne 0 ]; then
    echo "Error: $PPG_SCRIPT failed."
    echo "Error output: "
    cat "$TEMP_OUTPUT_FILE"  # Display the error output
    rm -f "$TEMP_OUTPUT_FILE"  # Clean up temporary file
    exit 1
fi

# Capture all the output from the temporary file
PPG_Output=$(cat "$TEMP_OUTPUT_FILE")
echo -e "PPG output: \n\n$PPG_Output"

# Clean up temporary file
rm -f "$TEMP_OUTPUT_FILE"

# echo "Running $ID_ALGORITHM..."
# ID_Output=$(python3 $ID_ALGORITHM "$PPG_Output")
# if [ $? -ne 0 ]; then
#     echo "Error: $ID_ALGORITHM failed."
#     exit 1
# fi


# python3 $OLED_SCRIPT "MESSAGE"
