#!/bin/bash

# Refresh db.csv
echo "Refreshing db.csv..."
cd utils
python3 refresh_db.py || { echo "Failed to refresh db.csv"; exit 1; }

# Run frontend server
echo "Running frontend server..."
cd ../frontend
python3 -m http.server