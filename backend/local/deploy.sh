#!/bin/bash

# Load environment variables from the .env file
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

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

# Check if the opensora image exists
model_image_id=$(sudo docker images -q opensora:latest)
if [ -z "$model_image_id" ]; then
    echo "opensora:latest image not found. Building the image..."
    # Assume you have already cloned Open-Sora repository and patched ckpt_utils.py
    cd Open-Sora
    sudo docker build -t opensora . || { echo "Failed to build opensora Docker image"; exit 1; }
else
    echo "opensora:latest image found."
fi

# Build the inference server image with the specific model name
echo "Building opensora_api Docker image..."
cd ../text2vid-viewer/backend/inference
sudo docker build --no-cache -t opensora_api . || { echo "Failed to build opensora_api Docker image"; exit 1; }

# Check images are built
echo ""
echo "Docker images:"
sudo docker images
echo ""

# Run the inference server with the specific model name
echo "Running opensora_api inference server..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^opensora_api$"; then
    sudo docker rm -f opensora_api || { echo "Failed to remove existing opensora_api Docker container"; exit 1; }
fi

# Run container opensora_api with environment variables
sudo docker run -d \
           -p 5000:5000 \
           --env-file .env \
           -v $DATA_DIR:/data \
           -v $LOGS_DIR:/app/logs \
           --name opensora_api \
           --gpus all \
           opensora_api:latest

echo "Deployment script completed successfully."
