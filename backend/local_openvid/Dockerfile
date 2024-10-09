FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    wget

# Set Python3 as default python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install PyTorch with CUDA 11.7
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Install other required Python packages
RUN pip install numpy tqdm Pillow boto3

# Clone OpenVid-1M repository
RUN git clone https://github.com/NJU-PCALab/OpenVid-1M.git /app/OpenVid-1M

# Download the model weights
WORKDIR /app/OpenVid-1M
RUN wget https://huggingface.co/nkp37/OpenVid-1M/resolve/main/model_weights/STDiT-16×512×512.pt

# Create the logs directory
RUN mkdir -p /app/logs && chmod -R 777 /app/logs
ENV PYTHONUNBUFFERED=1

# Copy the inference script
COPY backend/local/inference.py /app/inference.py

# Copy the prompt file
COPY prompts.txt /app/prompts.txt

# Set the working directory
WORKDIR /app

# Run the inference script with model argument
ENTRYPOINT ["python", "/app/inference.py"]
