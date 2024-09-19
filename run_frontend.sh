#!/bin/bash

# Check that .env file exists
if [ ! -f .env ]; then
    echo ".env file not found in dir root!"
    exit 1
fi

# Source the .env file
export $(grep -v '^#' .env | xargs)
echo "Sourced .env file"

# Refresh db.csv
echo "Refreshing db.csv..."
cd utils
python3 refresh_db.py || { echo "Failed to refresh db.csv"; exit 1; }

# Run frontend server
echo "Running frontend server..."
cd ../frontend
python3 -m http.server