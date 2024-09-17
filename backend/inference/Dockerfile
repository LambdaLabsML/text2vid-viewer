FROM shivamsphn/opensora:latest

# Install Flask
RUN pip install Flask

# Copy the .env file to the container
COPY /tmp/.env /app/.env

# Load environment variables from the .env file
ENV $(cat /app/.env | xargs)

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
CMD ["python", "/app/inference_api.py", "${MODEL_NAME}"]
