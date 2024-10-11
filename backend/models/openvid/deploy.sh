#!/bin/bash

# Load environment variables from the .env file
ENV_PATH="/home/ubuntu/text2vid-viewer/.env"
if [ -f "$ENV_PATH" ]; then
    export $(grep -v '^#' "$ENV_PATH" | xargs)
else
    echo "File not found: $ENV_PATH"
    exit 1
fi

# Variables
OPENVID_REPO="https://github.com/NJU-PCALab/OpenVid-1M.git"
OPENVID_DIR="/home/ubuntu/text2vid-viewer/backend/models/openvid/OpenVid-1M"
CHECKPOINT_URL="https://huggingface.co/nkp37/OpenVid-1M/resolve/main/model_weights/STDiT-16x512x512.pt"
CHECKPOINT_DIR="/home/ubuntu/text2vid-viewer/backend/models/openvid/checkpoints"


# Function to handle errors
handle_error() {
    echo "Error occurred in script at line: $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR


# Remove all containers
containers=$(sudo docker ps -qa)
if [ -n "$containers" ]; then
    echo "Removing all existing containers..."
    sudo docker rm -v -f $containers
else
    echo "No containers to remove"
fi

# Clone OpenVid repository if not exists
if [ ! -d "$OPENVID_DIR" ]; then
    echo "Cloning OpenVid-1M repository..."
    git clone --quiet $OPENVID_REPO $OPENVID_DIR > /dev/null || { echo "Failed to clone OpenVid-1M repository"; exit 1; }
else
    echo "OpenVid-1M directory already exists. Skipping clone."
fi

# Patch inference script
echo "Patching inference script..."
cp /home/ubuntu/text2vid-viewer/backend/models/openvid/inference.py $OPENVID_DIR/scripts/inference.py || { echo "Failed to patch inference script"; exit 1; }

# Build the openvid-inference image
echo "Building openvid-inference Docker image..."
cd /home/ubuntu/text2vid-viewer
sudo docker build --no-cache -t openvid-inference -f backend/models/openvid/Dockerfile . || { echo "Failed to build openvid-inference Docker image"; exit 1; }

# Download checkpoints
echo "Downloading model weights..."
mkdir -p $CHECKPOINT_DIR
cd $CHECKPOINT_DIR
curl -L -O $CHECKPOINT_URL || { echo "Failed to download model weights"; exit 1; }


# Run container openvid-inference
# Ensure any container with same name is removed first
echo "Running openvid-inference container..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^openvid_inference$"; then
    sudo docker rm -f openvid_inference || { echo "Failed to remove existing openvid-inference Docker container"; exit 1; }
fi


# Run the inference
echo "Running inference..."
sudo docker run \
    --rm \
    --gpus all \
    --env-file /home/ubuntu/text2vid-viewer/.env \
    -v $CHECKPOINT_DIR:/workspace/checkpoint \
    --name openvid_inference \
    openvid-inference:latest \
    torchrun --standalone --nproc_per_node=1 \
    /OpenVid-1M/scripts/inference.py \
    --config /OpenVid-1M/configs/stdit/inference/16x512x512.py \
    --ckpt-path /workspace/checkpoint/STDiT-16x512x512.pt