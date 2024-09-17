#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <model_name>"
    exit 1
fi

MODEL_NAME=$1

# Check if MODEL_NAME is valid
if [[ "$MODEL_NAME" != "lambda" && "$MODEL_NAME" != "opensora-v1-1" && "$MODEL_NAME" != "opensora-v1-2" ]]; then
    echo "Error: Invalid model name '${MODEL_NAME}'."
    echo "Allowed values are: lambda, opensora-v1-1, opensora-v1-2."
    exit 1
fi

HOSTNAME=ubuntu@209.20.156.111
KEY_PATH=~/.ssh/x1.pem

# Copy the .env file and deploy script to the remote host
echo "Copying .env and remote_setup.sh files to remote host..."
scp -v -i ${KEY_PATH} .env remote_setup.sh ${HOSTNAME}:/tmp/ || { echo "Failed to copy files to remote host"; exit 1; }

# Execute the deploy script on the remote host
ssh -i ${KEY_PATH} ${HOSTNAME} "chmod +x /tmp/remote_setup.sh && /tmp/remote_setup.sh ${MODEL_NAME}" || { echo "Failed to execute the setup script on remote host"; exit 1; }

echo "Script executed successfully on ${HOSTNAME}"
