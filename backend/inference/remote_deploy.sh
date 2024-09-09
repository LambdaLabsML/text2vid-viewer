#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <model_name> <hf_token>"
    exit 1
fi


MODEL_NAME=$1
HF_TOKEN=$2

# Check if MODEL_NAME is valid
if [[ "$MODEL_NAME" != "lambda" && "$MODEL_NAME" != "opensora-v1-1" && "$MODEL_NAME" != "opensora-v1-2" ]]; then
    echo "Error: Invalid model name '${MODEL_NAME}'."
    echo "Allowed values are: lambda, opensora-v1-1, opensora-v1-2."
    exit 1
fi

HOSTNAME=ubuntu@209.20.156.108
KEY_PATH=~/.ssh/x1.pem

# Copy the deploy script to the remote host and execute it with the model name and HF token arguments
scp -i ~/.ssh/x1.pem remote_setup.sh ${HOSTNAME}:/tmp/ && \
ssh -i ${KEY_PATH} ${HOSTNAME} "chmod +x /tmp/remote_setup.sh && /tmp/remote_setup.sh ${MODEL_NAME} ${HF_TOKEN}" || { echo "Failed to execute the setup script on remote host"; exit 1; }
echo "Script executed successfully on ${HOSTNAME}"
