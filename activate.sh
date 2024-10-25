#!/bin/bash

# Function to check if Python is installed

# Set up the Python virtual environment name (e.g., .venv)
VENV_DIR=".venv"

# Check if virtual environment exists, if not, create one
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists in $VENV_DIR."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Check if the requirements.txt file exists
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No requirements.txt file found. Skipping package installation."
fi

echo "Virtual environment activated and packages installed."


