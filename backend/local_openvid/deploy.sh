#!/bin/bash

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --model)
            MODEL="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Load environment variables from the .env file
ENV_PATH="/home/ubuntu/text2vid-viewer/.env"
if [ -f $ENV_PATH ]; then
    export $(cat $ENV_PATH | xargs)
else
    echo "File not found: $ENV_PATH"
    exit 1
fi

# Variables
OPENVID_REPO="https://github.com/NJU-PCALab/OpenVid-1M.git"
OPENVID_DIR="OpenVid-1M"

# Function to handle errors
handle_error() {
    echo "Error occurred in script at line: $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR

# Ensure required directories exist
echo "Setting up /data and /logs directories..."
DATA_DIR="/data"
LOGS_DIR="/logs"
sudo mkdir -p $DATA_DIR $LOGS_DIR
sudo chown $USER:$USER $DATA_DIR $LOGS_DIR

# Remove all containers
containers=$(sudo docker ps -qa)
if [ -n "$containers" ]; then
    echo "Removing all existing containers..."
    sudo docker rm -v -f $containers
else
    echo "No containers to remove"
fi

# Clone OpenVid-1M repository if not exists
if [ ! -d "$OPENVID_DIR" ]; then
    git clone --quiet $OPENVID_REPO > /dev/null || { echo "Failed to clone OpenVid-1M repository"; exit 1; }
else
    echo "OpenVid-1M directory already exists. Skipping clone."
fi

# Build the openvid-inference image
echo "Building openvid-inference Docker image..."
cd /home/ubuntu/text2vid-viewer
sudo docker build --no-cache -t openvid-inference -f backend/local/Dockerfile . || { echo "Failed to build openvid-inference Docker image"; exit 1; }

# Run container openvid-inference
# Ensure any container with same name is removed first
echo "Running openvid-inference container..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^openvid_inference$"; then
    sudo docker rm -f openvid_inference || { echo "Failed to remove existing openvid-inference Docker container"; exit 1; }
fi

# Run the inference
sudo docker run \
    --rm \
    --gpus all \
    --env-file /home/ubuntu/text2vid-viewer/.env \
    -v /home/ubuntu/data:/data \
    -v /home/ubuntu/logs:/app/logs \
    --name openvid_inference \
    openvid-inference:latest \
    --model ${MODEL}
