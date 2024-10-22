#!/bin/bash

# Check that .env file exists
if [ ! -f .env ]; then
    echo ".env file not found in dir root!"
    exit 1
fi

# Source the .env file
export $(grep -v '^#' .env | xargs)
echo "Sourced .env file"


# Make sure pip is installed
if ! command -v pip &> /dev/null; then
    echo "Pip not found. Installing pip"
    sudo apt-get update
    sudo apt-get install python3-pip -y || { echo "Failed to install pip"; exit 1; }
fi

# Install dependencies
python3 -m pip install --upgrade pip flatbuffers
python3 -m pip install boto3 python-dotenv pandas || { echo "Failed to install dependencies"; exit 1; }
echo "Installed dependencies"

# Refresh db.csv
python3 backend/utils/refresh_db.py || { echo "Failed to refresh db.csv"; exit 1; }
echo "Refreshed db.csv"

# Run frontend server
echo "Running frontend server"
cd frontend
python3 -m http.server 8000