#!/bin/bash

HOSTNAME=ubuntu@209.20.156.108
KEY_PATH=~/.ssh/x1.pem

# Copy the deploy script to the remote host and execute it using the SSH alias
scp -i ~/.ssh/x1.pem remote_setup.sh ${HOSTNAME}:/tmp/ && \
ssh -i ${KEY_PATH} ${HOSTNAME} 'chmod +x /tmp/remote_setup.sh && /tmp/remote_setup.sh' || { echo "Failed to execute the setup script on remote host"; exit 1; }
echo "Script executed successfully on ${HOSTNAME}"
