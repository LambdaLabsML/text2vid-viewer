#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error occurred in script at line: $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR

# Default hostname alias
DEFAULT_HOSTNAME="imageeval"

# Read hostname parameter or use default
HOSTNAME="${1:-$DEFAULT_HOSTNAME}"

# Copy the deploy script to the remote host and execute it using the SSH alias
scp remote_setup.sh ${HOSTNAME}:/tmp/ && \
ssh ${HOSTNAME} 'chmod +x /tmp/remote_setup.sh && /tmp/remote_setup.sh' || { echo "Failed to execute the setup script on remote host"; exit 1; }
echo "Script executed successfully on ${HOSTNAME}"
