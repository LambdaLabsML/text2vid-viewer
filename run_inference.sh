#!/bin/bash

# Set default value for MODEL
MODEL="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --model)
            MODEL="$2"
            shift # past argument
            shift # past value
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Print the selected model for confirmation (optional)
echo "Model set to: $MODEL"

ROOT_DIR="/home/ubuntu"
MODEL_CONFIG="/home/ubuntu/text2vid-viewer/backend/configs/$MODEL.py"
PROMPT_PATH="/home/ubuntu/text2vid-viewer/prompts.txt"
DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/local/deploy.sh"

cd $ROOT_DIR

# Check model has a valid config file (unless all models are selected)
if [ "$MODEL" != "all" ]; then
    if [ ! -f "$MODEL_CONFIG" ]; then
        echo "Model config file not found at ${MODEL_CONFIG}"
        exit 1
    fi
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