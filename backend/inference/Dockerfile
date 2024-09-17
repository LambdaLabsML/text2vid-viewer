FROM shivamsphn/opensora:latest

# Install Flask
RUN pip install Flask boto3

# Create the logs directory
RUN mkdir -p /app/logs && chmod -R 777 /app/logs
ENV PYTHONUNBUFFERED=1

# Copy the .env file to the container
COPY .env /app/.env

# Load environment variables from the .env file
ENV $(grep -v '^#' /app/.env | xargs)

# Explicitly set the Hugging Face token as an environment variable (already done by .env, but just to be sure)
ENV HUGGINGFACE_HUB_TOKEN=${HUGGINGFACE_HUB_TOKEN}

# Ensure that the Hugging Face CLI can pick up the token
RUN mkdir -p /root/.huggingface && echo "{ \"token\": \"${HUGGINGFACE_HUB_TOKEN}\" }" > /root/.huggingface/token.json

# Copy the Flask API server script
COPY inference_api.py /app/inference_api.py

# Copy the entire config directory
COPY configs/ /app/custom_configs/

# Set the environment variable for save directory
ENV SAVE_DIR="/data"

# Build argument for model name
ARG MODEL_NAME

# Expose the port the API server will run on
EXPOSE 5000

# Run the API server with the model name argument
CMD ["python", "/app/inference_api.py"]
