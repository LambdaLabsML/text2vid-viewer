# Use the official NVIDIA CUDA image with Ubuntu 20.04
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# Install Python 3.10
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils python3.10-venv && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Install pip for Python 3.10
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Install necessary packages
RUN apt-get install -y \
    git \
    wget \
    ninja-build

# Install PyTorch with CUDA 11.7 support for Python 3.10
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu117

# Install other required Python packages
RUN pip install packaging
RUN pip install flash-attn --no-build-isolation
RUN pip install -v --disable-pip-version-check --no-cache-dir --no-build-isolation \
    --config-settings "--build-option=--cpp_ext" \
    --config-settings "--build-option=--cuda_ext" \
    git+https://github.com/NVIDIA/apex.git
RUN pip install -U xformers --index-url https://download.pytorch.org/whl/cu121
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
