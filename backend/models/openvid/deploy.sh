#!/bin/bash

# Load environment variables from the .env file
ENV_PATH="/home/ubuntu/text2vid-viewer/.env"
if [ -f "$ENV_PATH" ]; then
    export $(grep -v '^#' "$ENV_PATH" | xargs)
else
    echo "Error: .env file not found at $ENV_PATH"
    exit 1
fi

# Variables
OPENVID_REPO="https://github.com/NJU-PCALab/OpenVid-1M.git"
PROJECT_DIR="/home/ubuntu/text2vid-viewer"
OPENVID_DIR="$PROJECT_DIR/backend/models/openvid/OpenVid-1M"
CHECKPOINT_URL="https://huggingface.co/nkp37/OpenVid-1M/resolve/main/model_weights/STDiT-16x512x512.pt"
CHECKPOINT_DIR="$PROJECT_DIR/backend/models/openvid/checkpoints"

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
    echo "No containers to remove."
fi

# Build the openvid-inference image
echo "Building openvid-inference Docker image..."
cd "$PROJECT_DIR"
sudo docker build --no-cache -t openvid-inference -f backend/models/openvid/Dockerfile . || { echo "Error: Docker image build failed"; exit 1; }

# Download checkpoints
echo "Downloading model weights..."
mkdir -p "$CHECKPOINT_DIR"
cd "$CHECKPOINT_DIR"
curl -L -O "$CHECKPOINT_URL" || { echo "Error: Failed to download model weights"; exit 1; }

# Run container openvid-inference
# Ensure any container with same name is removed first
echo "Running openvid-inference container..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^openvid_inference$"; then
    sudo docker rm -f openvid_inference || { echo "Error: Failed to remove existing openvid-inference Docker container"; exit 1; }
fi

# Run the inference
echo "Starting inference..."
sudo docker run \
    --rm \
    --gpus all \
    --env-file "$ENV_PATH" \
    -v "$CHECKPOINT_DIR:/workspace/checkpoint" \
    --name openvid_inference \
    openvid-inference:latest \
    torchrun --standalone --nproc_per_node=1 \
    /OpenVid-1M/scripts/inference.py \
    --config /OpenVid-1M/configs/stdit/inference/16x512x512.py \
    --ckpt-path /workspace/checkpoint/STDiT-16x512x512.pt \
    --prompt_path /prompts.txt || { echo "Error: Inference run failed"; exit 1; }

echo "Inference completed successfully."
