#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <model_name> <hf_token>"
    exit 1
fi

MODEL_NAME=$1
HF_TOKEN=$2

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
IMAGE_NAME="${MODEL_NAME}"
CONTAINER_NAME="${MODEL_NAME}_api"

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

# Check if the specific model image exists
model_image_id=$(sudo docker images -q ${IMAGE_NAME}:latest)
if [ -n "$model_image_id" ]; then
    echo "${IMAGE_NAME}:latest image found. Removing all other docker images..."
    all_images=$(sudo docker images -q)
    for image in $all_images; do
        if [ "$image" != "$model_image_id" ]; then
            sudo docker rmi -f $image
        fi
    done
else
    echo "${IMAGE_NAME}:latest image not found. Removing all docker images and repositories..."
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
    echo "Building ${IMAGE_NAME} Docker image..."
    sudo docker build -t $IMAGE_NAME --build-arg MODEL_NAME=${MODEL_NAME} -f Dockerfile . || { echo "Failed to build ${IMAGE_NAME} Docker image"; exit 1; }
fi

# Build the inference server image with the specific model name
echo "Building ${IMAGE_NAME}_api Docker image..."
cd /home/ubuntu/text2vid-viewer/backend/inference
sudo docker build -t ${IMAGE_NAME}_api --build-arg MODEL_NAME=${MODEL_NAME} --build-arg HF_TOKEN=${HF_TOKEN} . || { echo "Failed to build ${IMAGE_NAME}_api Docker image"; exit 1; }

# Run the inference server with the specific model name
echo "Running ${IMAGE_NAME}_api inference server..."
sudo docker run -d --gpus all -p 5000:5000 -v /home/ubuntu/data:/data --name $CONTAINER_NAME ${IMAGE_NAME}_api:latest || { echo "Failed to run ${IMAGE_NAME}_api Docker container"; exit 1; }

echo "Deployment script completed successfully."


# Print example request
echo ''
echo "Example request:"
echo '```'
echo ''
echo "$ curl -X POST http://129.146.68.60:5000/generate -H \"Content-Type: application/json\" -d '{
        \"config\": \"lambda.py\",
        \"save_dir\" : \"/data\"
    }' --output /tmp/opensora_sample.mp4"
echo '```'
echo ''
