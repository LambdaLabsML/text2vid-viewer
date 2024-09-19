#!/bin/bash

# Load environment variables from the .env file
if [ -f ".env" ]; then
    export $(cat .env | xargs)
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

# Clone OpenSora repository
echo "Cloning OpenSora repository..."
if [ -d "Open-Sora" ]; then
    echo "Removing existing Open-Sora directory..."
    rm -rf Open-Sora
fi
git clone $OPEN_SORA_REPO || { echo "Failed to clone OpenSora repository"; exit 1; }

# Replace ckpt_utils.py with the patched version
echo "Patching ckpt_utils.py..."
PATCH_URL="https://raw.githubusercontent.com/LambdaLabsML/text2vid-viewer/main/backend/ckpt_utils_patch.py"
PATCH_FILE="Open-Sora/opensora/utils/ckpt_utils.py"
# Download the patched file and replace the original ckpt_utils.py
curl -o $PATCH_FILE $PATCH_URL || { echo "Failed to download the patch for ckpt_utils.py"; exit 1; }

cd Open-Sora
echo "Building opensora Docker image..."
sudo docker build -t opensora -f Dockerfile . || { echo "Failed to build opensora Docker image"; exit 1; }

# Build the inference server image with the specific model name
echo "Building opensora-inference Docker image..."
cd /home/ubuntu/text2vid-viewer/backend/local
sudo docker build --no-cache -t opensora-inference . || { echo "Failed to build opensora-inference Docker image"; exit 1; }

# Check images are built
echo ""
echo "Docker images:"
sudo docker images
echo ""

# Run the inference server with the specific model name
echo "Running opensora-inference container..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^opensora-inference$"; then
    sudo docker rm -f opensora-inference || { echo "Failed to remove existing opensora-inference Docker container"; exit 1; }
fi

# Run container opensora-inference with environment variables
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/data \  # Mount the data directory
  -v $(pwd)/prompts.txt:/app/prompts.txt \  # Mount the prompts file
  -v $(pwd)/logs:/app/logs \  # Mount the logs directory
  opensora-inference \
  --model your_model_name \
  --prompt-path /app/prompts.txt

echo "Deployment script completed successfully."
