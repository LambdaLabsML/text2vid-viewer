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
        --prompt-path)
            PROMPT_PATH="$2"
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
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

# Variables
OPEN_SORA_REPO="https://github.com/hpcaitech/Open-Sora.git"
IMAGE_EVAL_REPO="https://github.com/LambdaLabsML/text2vid-viewer.git"
OPEN_SORA_DIR="Open-Sora"

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

# Clone OpenSora repository if not exists
# if [ ! -d "$OPEN_SORA_DIR" ]; then
#     echo "Cloning OpenSora repository..."
#     git clone $OPEN_SORA_REPO || { echo "Failed to clone OpenSora repository"; exit 1; }
# else
#     echo "Open-Sora directory already exists. Skipping clone."
# fi

# # Replace ckpt_utils.py with the patched version
# echo "Patching ckpt_utils.py..."
# PATCH_URL="https://raw.githubusercontent.com/LambdaLabsML/text2vid-viewer/main/backend/ckpt_utils_patch.py"
# PATCH_FILE="$OPEN_SORA_DIR/opensora/utils/ckpt_utils.py"
# # Download the patched file and replace the original ckpt_utils.py
# curl -o $PATCH_FILE $PATCH_URL || { echo "Failed to download the patch for ckpt_utils.py"; exit 1; }

# cd $OPEN_SORA_DIR
# echo "Building opensora Docker image..."
# sudo docker build -t opensora -f Dockerfile . || { echo "Failed to build opensora Docker image"; exit 1; }

# Build the inference server image with the specific model name
echo "Building opensora-inference Docker image..."
cd /home/ubuntu/text2vid-viewer/backend
sudo docker build --no-cache -t opensora-inference -f local/Dockerfile . || { echo "Failed to build opensora-inference Docker image"; exit 1; }


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

# # Construct the docker run command
# DOCKER_RUN_CMD="sudo docker run --rm \
#   --env-file /home/ubuntu/text2vid-viewer/.env \
#   -v /home/ubuntu/data:/data \  # Mount the data directory
#   -v ${PROMPT_PATH}:/app/prompts.txt \  # Mount the prompts file
#   -v /home/ubuntu/logs:/app/logs \  # Mount the logs directory
#   opensora-inference \
#   --model ${MODEL} \
#   --prompt-path /app/prompts.txt"

# # Echo the constructed command
# echo "Running the following command:"
# echo "$DOCKER_RUN_CMD"

# # Execute the command
# eval "$DOCKER_RUN_CMD"

# # Run container opensora-inference with environment variables
sudo docker run --rm \
  --env-file /home/ubuntu/text2vid-viewer/.env \
  -v /home/ubuntu/data:/data \
  -v /home/ubuntu/logs:/app/logs \
  opensora-inference \
  --model opensora-v1-2

echo "Deployment script completed successfully."
