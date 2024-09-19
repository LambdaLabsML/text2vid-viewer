#!/bin/bash
HOSTNAME=ubuntu@209.20.156.111
KEY_PATH=~/.ssh/x1.pem

# Refresh db.csv
echo "Refreshing db.csv..."
python3 ../utils/refresh_db.py || { echo "Failed to refresh db.csv"; exit 1; }

# Copy the .env file and deploy script to the remote host
echo "Copying .env and remote_setup.sh files to remote host..."
scp -i ${KEY_PATH} ../frontend/db.csv .env remote_setup.sh prompts.txt ${HOSTNAME}:/tmp/ || { echo "Failed to copy files to remote host"; exit 1; }

# Execute the deploy script on the remote host
ssh -i ${KEY_PATH} ${HOSTNAME} "chmod +x /tmp/remote_setup.sh && /tmp/remote_setup.sh" || { echo "Failed to execute the setup script on remote host"; exit 1; }

echo "Script executed successfully on ${HOSTNAME}"

# Print example request
echo ''
echo "Example requests:"
echo '```'
echo "$ curl -X POST http://209.20.156.111:5000/generate -H \"Content-Type: application/json\" -d '{
        \"model\": \"lambda\",
        \"prompt\": \"a woman dancing\"
    }'"
echo ''
echo "$ curl -X POST http://209.20.156.111:5000/generate -H \"Content-Type: application/json\" -d '{
        \"model\": \"lambda\",
        \"prompt\": [\"a woman dancing\", \"a beautiful waterfall\"]
    }'"
echo '```'
echo ''