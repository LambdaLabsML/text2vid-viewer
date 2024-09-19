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

# Check model has a valid config file
if [ ! -f backend/configs/$MODEL.py ]; then
    echo "Model config file not found at backend/configs/${$MODEL}.py"
    exit 1
fi

# Check prompt file exists
PROMPT_PATH="backend/prompts.txt"
if [ ! -f $PROMPT_PATH ]; then
    echo "Prompt file not found!"
    exit 1
fi

# Run opensora-inference
echo "Running opensora-inference..."
/bin/bash backend/local/deploy.sh --model $MODEL --prompt-path $PROMPT_PATH

echo "inference completed"