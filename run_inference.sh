#!/bin/bash

MODEL="all" # Set default value for MODEL
ROOT_DIR="/home/ubuntu"
ENV_PATH="/home/ubuntu/text2vid-viewer/.env"
PROMPT_TXT_PATH="/home/ubuntu/text2vid-viewer/prompts.txt"
PROMPT_CSV_PATH="/home/ubuntu/text2vid-viewer/prompts.csv"

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



# Load environment variables from the .env file
if [ -f $ENV_PATH ]; then
    export $(cat $ENV_PATH | xargs)
else
    echo "file not found: $ENV_PATH"
    exit 1
fi

# Print the selected model for confirmation (optional)
echo "Model set to: $MODEL"

cd "$ROOT_DIR"

# Throw error if prompts.csv and prompts.txt do not exist
if [ ! -f "$PROMPT_CSV_PATH" && ! -f "$PROMPT_TXT_PATH" ]; then 
    echo "Prompt file not found at ${PROMPT_CSV_PATH} or ${PROMPT_TXT_PATH}"
    exit 1
fi

# Define PROMPT_PATH as PROMPT_CSV_PATH if exists, else PROMPT_TXT_PATH
PROMPT_PATH="$PROMPT_CSV_PATH"
if [ ! -f "$PROMPT_CSV_PATH" ]; then
    PROMPT_PATH="$PROMPT_TXT_PATH"
fi

# Make prompts.csv filename safe (if exists)
# Convert prompts.csv to prompts.txt (if exists)
# Make prompts.txt filename safe
echo "Preprocessing prompts..."
python /home/ubuntu/text2vid-viewer/backend/utils/validate_prompts.py --prompt_path "$PROMPT_PATH" || { echo "Invalid prompts"; exit 1; }

# Install backend dependencies (that are common across models)
pip install boto3 python-dotenv pandas || { echo "Failed to install dependencies"; exit 1; }

# Create log and data directories owned by ubuntu
mkdir -p /home/ubuntu/logs /home/ubuntu/data

# Determine which deploy script to use based on the model
if [ "$MODEL" == "openvid" ]; then
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/models/openvid/deploy.sh"
    echo "Using deploy script for openvid model: $DEPLOY_SCRIPT"
elif [ "$MODEL" == "cog" ]; then
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/models/cog/deploy.sh"
    echo "Using deploy script for cog model: $DEPLOY_SCRIPT"
elif [ "$MODEL" == "pyramidflow" ]; then
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/models/pyramidflow/deploy.sh"
    echo "Using deploy script for cog model: $DEPLOY_SCRIPT"
else
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/models/opensora/deploy.sh"
    echo "Using deploy script for model: $MODEL"
    # Check if model has a valid config file (unless all models are selected)
    MODEL_CONFIG="/home/ubuntu/text2vid-viewer/backend/models/opensora/configs/$MODEL.py"
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

# Export generated videos to S3
echo "Exporting videos to S3..."
python /home/ubuntu/text2vid-viewer/backend/utils/s3_export.py --model "$MODEL" --prompt_csv "$PROMPT_CSV_PATH" || { echo "Failed to export videos to S3"; exit 1; }

echo "Inference completed"
