#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error occurred in script at line: $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR

# Variables
OPEN_SORA_REPO="https://github.com/hpcaitech/Open-Sora.git"
IMAGE_EVAL_REPO="https://github.com/LambdaLabsML/text2vid-viewer.git"
IMAGE_NAME="opensora"
CONTAINER_NAME="opensora_api"

# Ensure required directories exist
echo "Checking required directories..."
if [ -d "/home/ubuntu/data" ]; then
    echo "Removing existing /home/ubuntu/data directory..."
    sudo rm -rf /home/ubuntu/data
fi
echo "Creating /home/ubuntu/data directory..."
sudo mkdir -p /home/ubuntu/data
sudo chown $USER:$USER /home/ubuntu/data

# Remove all containers
containers=$(sudo docker ps -qa)
if [ -n "$containers" ]; then
    sudo docker rm -v -f $containers
else
    echo "No containers to remove"
fi

# Update inference server code
cd ~
if [ -d "text2vid-viewer" ]; then
    echo "Removing existing text2vid-viewer directory..."
    rm -rf text2vid-viewer
fi
git clone $IMAGE_EVAL_REPO || { echo "Failed to clone text2vid-viewer repository"; exit 1; }

# Check if opensora:latest exists
opensora_image_id=$(sudo docker images -q opensora:latest)
if [ -n "$opensora_image_id" ]; then
    echo "opensora:latest image found. Removing all other docker images..."
    all_images=$(sudo docker images -q)
    for image in $all_images; do
        if [ "$image" != "$opensora_image_id" ]; then
            sudo docker rmi -f $image
        fi
    done
else
    echo "opensora:latest image not found. Removing all docker images and repositories..."
    all_images=$(sudo docker images -q)
    if [ -n "$all_images" ]; then
        sudo docker rmi -f $all_images
    else
        echo "No images to remove"
    fi


    # Clone OpenSora repository
    echo "Cloning OpenSora repository..."
    if [ -d "Open-Sora" ]; then
        echo "Removing existing Open-Sora directory..."
        rm -rf Open-Sora
    fi
    git clone $OPEN_SORA_REPO || { echo "Failed to clone OpenSora repository"; exit 1; }
    cd Open-Sora
    echo "Building OpenSora Docker image..."
    sudo docker build -t $IMAGE_NAME -f Dockerfile . || { echo "Failed to build OpenSora Docker image"; exit 1; }
fi

# Build OpenSora inference server image
echo "Building OpenSora inference server Docker image..."
cd text2vid-viewer/backend/inference
sudo docker build -t ${IMAGE_NAME}_api . || { echo "Failed to build OpenSora inference server Docker image"; exit 1; }

# Run the inference server
echo "Running OpenSora inference server..."
sudo docker run -d --gpus all -p 5000:5000 -v /home/ubuntu/data:/data --name $CONTAINER_NAME ${IMAGE_NAME}_api:latest || { echo "Failed to run OpenSora inference server Docker container"; exit 1; }

echo "Deployment script completed successfully."

# Print example request
echo "You can make a request to the inference server using the following command:"
echo '```'
echo "$ SERVER_IP=<...>"
echo ''
echo "$ curl -X POST http://\${SERVER_IP}:5000/generate -H \"Content-Type: application/json\" -d '{
        \"num_frames\": \"24\",
        \"resolution\": \"240p\",
        \"aspect_ratio\": \"16:9\",
        \"prompt\": \"a beautiful sunset\",
        \"save_dir\" : \"/data\"
    }' --output /tmp/opensora_sample.mp4"
echo '```'
echo ''
