# Use the official NVIDIA CUDA image with Ubuntu 20.04
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    wget

# Set Python3 as default python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install PyTorch with CUDA 11.7 support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Install other required Python packages
RUN pip install numpy tqdm Pillow boto3

# Set the working directory
WORKDIR /app

# Clone the OpenVid-1M repository
RUN git clone https://github.com/NJU-PCALab/OpenVid-1M.git /app/OpenVid-1M

# Download the model weights
RUN wget -P /app/OpenVid-1M https://your-model-weights-url/STDiT-16x1024x1024.pt

# Create the logs directory
RUN mkdir -p /app/logs && chmod -R 777 /app/logs
ENV PYTHONUNBUFFERED=1

# Copy the inference script
COPY backend/local_openvid/inference.py /app/inference.py

# Copy the prompt file
COPY prompts.txt /app/prompts.txt

# Expose the data directory as a volume
VOLUME ["/data"]

# Set the working directory
WORKDIR /app

# Run the inference script
ENTRYPOINT ["python", "/app/inference.py"]