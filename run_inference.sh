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

ROOT_DIR="/home/ubuntu"
MODEL_CONFIG="/home/ubuntu/text2video-viewer/backend/configs/$MODEL.py"
PROMPT_PATH="/home/ubuntu/text2video-viewer/backend/prompts.txt"
DEPLOY_SCRIPT = "/home/ubuntu/text2video-viewer/backend/local/deploy.sh"

cd $ROOT_DIR

# Check model has a valid config file
if [ ! -f $MODEL_CONFIG ]; then
    echo "Model config file not found at ${MODEL_CONFIG}"
    exit 1
fi

# Check prompt file exists
if [ ! -f $PROMPT_PATH ]; then
    echo "Prompt file not found!"
    exit 1
fi

# Run opensora-inference
echo "Running opensora-inference..."
cd /home/ubuntu
/bin/bash ${DEPLOY_SCRIPT} --model $MODEL

echo "inference completed"