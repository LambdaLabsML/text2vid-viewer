#!/bin/bash

# Check that .env file exists
if [ ! -f .env ]; then
    echo ".env file not found in dir root!"
    exit 1
fi

# Source the .env file
export $(grep -v '^#' .env | xargs)
echo "Sourced .env file"

# Make sure venv is installed
apt install python3.12-venv

# Make sure pip and venv are installed
if ! command -v pip &> /dev/null; then
    echo "Pip not found. Installing pip"
    sudo apt-get update
    sudo apt-get install python3-pip python3-venv -y || { echo "Failed to install pip or venv"; exit 1; }
fi

# Create a virtual environment if not already created
if [ ! -d "venv" ]; then
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
    echo "Created virtual environment"
fi

# Activate the virtual environment
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
echo "Activated virtual environment"

# Upgrade pip inside the virtual environment
python3 -m pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }

# Install dependencies in the virtual environment
python3 -m pip install flatbuffers boto3 python-dotenv pandas || { echo "Failed to install dependencies"; exit 1; }
echo "Installed dependencies"

# Refresh db.csv
python3 backend/utils/refresh_db.py || { echo "Failed to refresh db.csv"; exit 1; }
echo "Refreshed db.csv"

# Run frontend server
echo "Running frontend server"
cd frontend
python3 -m http.server 8000
