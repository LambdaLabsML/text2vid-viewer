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
PROMPT_PATH="/home/ubuntu/text2vid-viewer/prompts.txt"

cd $ROOT_DIR

# Check prompt file exists
if [ ! -f "$PROMPT_PATH" ]; then
    echo "Prompt file not found at ${PROMPT_PATH}"
    exit 1
fi

# Determine which deploy script to use based on the model
if [ "$MODEL" == "openvid" ]; then
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/local_openvid/deploy.sh"
    echo "Using deploy script for openvid model: $DEPLOY_SCRIPT"
else
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/local/deploy.sh"
    echo "Using deploy script for model: $MODEL"
    # Check model has a valid config file (unless all models are selected)
    MODEL_CONFIG="/home/ubuntu/text2vid-viewer/backend/configs/$MODEL.py"
    if [ "$MODEL" != "all" ]; then
        if [ ! -f "$MODEL_CONFIG" ]; then
            echo "Model config file not found at ${MODEL_CONFIG}"
            exit 1
        fi
    fi
fi

# Run the deploy script with the specified model
echo "Running inference..."
/bin/bash "${DEPLOY_SCRIPT}" --model "$MODEL"

echo "Inference completed"
