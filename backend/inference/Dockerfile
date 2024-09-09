FROM kutanov/opensora:latest

# Install Flask
RUN pip install Flask

# Copy the Flask API server script
COPY inference_api.py .

# Copy the entire config directory
COPY configs/ configs/

# Set the environment variable for save directory
ENV SAVE_DIR="/data"

# Build argument for model name
ARG MODEL_NAME
ARG HF_TOKEN

# Set the HF_TOKEN environment variable
ENV HF_TOKEN=${HF_TOKEN}

# Expose the port the API server will run on
EXPOSE 5000

# Run the API server with the model name argument
CMD ["python", "inference_api.py", "${MODEL_NAME}"]