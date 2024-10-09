# Use the official NVIDIA CUDA image with Ubuntu 20.04
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# Set environment variables to suppress interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install necessary packages and Python 3.10
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.10 \
        python3.10-dev \
        python3.10-distutils \
        python3.10-venv \
        git \
        wget \
        ninja-build \
        build-essential \
        libpython3.10-dev && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.10
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Install PyTorch with CUDA 11.7 support for Python 3.10
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu117

# Install other required Python packages
RUN pip install packaging
RUN pip install flash-attn --no-build-isolation

# Install apex
RUN git clone https://github.com/NVIDIA/apex.git /tmp/apex && \
    cd /tmp/apex && \
    pip install -v --disable-pip-version-check --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" . && \
    cd / && rm -rf /tmp/apex

# Install xformers
RUN pip install -U xformers --index-url https://download.pytorch.org/whl/cu117

# Install additional Python packages
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
