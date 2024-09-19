#FROM shivamsphn/opensora:latest
FROM opensora:latest

# Install necessary libraries
RUN pip install boto3

# Create the logs directory
RUN mkdir -p /app/logs && chmod -R 777 /app/logs
ENV PYTHONUNBUFFERED=1

# Copy the inference script
COPY local/inference.py /app/inference.py

# Copy the entire config directory
COPY /configs/ /app/custom_configs/

# Set the environment variable for save directory
ENV SAVE_DIR="/data"

# Copy the prompt file
COPY prompts.txt /data/prompts.txt

# Run the inference script with model and prompt-path arguments
ENTRYPOINT ["python", "/app/inference.py"]
