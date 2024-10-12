# Base image with CUDA 12.1
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Create the Conda environment with Python 3.10
RUN conda create -n openvid python=3.10 -y && conda clean -a

# Activate the conda environment and install Python dependencies
SHELL ["conda", "run", "-n", "openvid", "/bin/bash", "-c"]
RUN pip install --upgrade pip && \
    pip install torch torchvision && \
    pip install packaging ninja && \
    pip install flash-attn --no-build-isolation && \
    pip install -v --disable-pip-version-check --no-cache-dir --no-build-isolation --config-settings "--build-option=--cpp_ext" --config-settings "--build-option=--cuda_ext" git+https://github.com/NVIDIA/apex.git && \
    pip install -U xformers --index-url https://download.pytorch.org/whl/cu121 && \
    pip install ipdb

# Clone the OpenVid-1M repository and install its requirements
RUN git clone https://github.com/NJU-PCALab/OpenVid-1M.git && \
    cd OpenVid-1M && \
    pip install -r requirements.txt

# Set the PYTHONPATH to include the OpenVid repo
ENV PYTHONPATH="${PYTHONPATH}:/OpenVid-1M"

# Patch the inference script
COPY backend/models/openvid/inference.py /OpenVid-1M/scripts/inference.py

# Copy the prompt file
COPY prompts.txt /prompts.txt

# Set the entry point to activate the conda environment before executing any command
ENTRYPOINT [ "conda", "run", "-n", "openvid", "/bin/bash", "-c" ]

# Command to keep the container alive, modify as needed
CMD ["bash"]
