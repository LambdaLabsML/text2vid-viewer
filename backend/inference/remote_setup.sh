#!/bin/bash

# Load environment variables from the .env file
if [ -f /tmp/.env ]; then
    export $(cat /tmp/.env | xargs)
else
    echo ".env file not found!"
    exit 1
fi


# Variables
OPEN_SORA_REPO="https://github.com/hpcaitech/Open-Sora.git"
IMAGE_EVAL_REPO="https://github.com/LambdaLabsML/text2vid-viewer.git"

# Function to handle errors
handle_error() {
    echo "Error occurred in script at line: $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR

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
cd /home/ubuntu
if [ -d "text2vid-viewer" ]; then
    echo "Removing existing text2vid-viewer directory..."
    rm -rf text2vid-viewer
fi
git clone $IMAGE_EVAL_REPO || { echo "Failed to clone text2vid-viewer repository"; exit 1; }

# Move .env to the build context directory (assuming text2vid-viewer is the context)
echo "Moving .env file to the build context..."
mv /tmp/.env /home/ubuntu/text2vid-viewer/backend/inference/.env || { echo "Failed to move .env file to build context"; exit 1; }


# Check if the specific model image exists
model_image_id=$(sudo docker images -q opensora:latest)
if [ -n "$model_image_id" ]; then
    echo "opensora:latest image found. Removing all other docker images..."
    all_images=$(sudo docker images -q)
    for image in $all_images; do
        if [ "$image" != "$model_image_id" ]; then
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

    # Replace ckpt_utils.py with the patched version
    echo "Patching ckpt_utils.py..."
    PATCH_URL="https://raw.githubusercontent.com/LambdaLabsML/text2vid-viewer/main/backend/inference/ckpt_utils_patch.py"
    PATCH_FILE="Open-Sora/opensora/utils/ckpt_utils.py"
    # Download the patched file and replace the original ckpt_utils.py
    curl -o $PATCH_FILE $PATCH_URL || { echo "Failed to download the patch for ckpt_utils.py"; exit 1; }

    cd Open-Sora
    echo "Building opensora Docker image..."
    sudo docker build -t opensora -f Dockerfile . || { echo "Failed to build opensora Docker image"; exit 1; }
fi

# Build the inference server image with the specific model name
echo "Building opensora_api Docker image..."
cd /home/ubuntu/text2vid-viewer/backend/inference
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
           --env-file /home/ubuntu/text2vid-viewer/backend/inference/.env \
           -v /home/ubuntu/data:/data \
           -v /home/ubuntu/logs:/app/logs \
           --name opensora_api \
           --gpus all \
           opensora_api:latest


echo "Deployment script completed successfully."
