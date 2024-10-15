# Base image with CUDA
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    /opt/conda/bin/conda clean -a

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Create the Conda environment with specified Python version
RUN conda create -n openvid python=3.10 -y && \
    conda clean -a

# Activate the conda environment and install Python dependencies
SHELL ["conda", "run", "-n", "openvid", "/bin/bash", "-c"]
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121 && \
    python -m pip install --no-cache-dir packaging ninja && \
    python -m pip install --no-cache-dir flash-attn --no-build-isolation && \
    python -m pip install --no-cache-dir -v --disable-pip-version-check --no-build-isolation \
    --config-settings "--build-option=--cpp_ext" \
    --config-settings "--build-option=--cuda_ext" \
    git+https://github.com/NVIDIA/apex.git && \
    python -m pip install --no-cache-dir -U xformers --index-url https://download.pytorch.org/whl/cu121 && \
    python -m pip install --no-cache-dir ipdb pandas --root-user-action=ignore

# Clone the OpenVid-1M repository and install its requirements
RUN git clone https://github.com/NJU-PCALab/OpenVid-1M.git /OpenVid-1M && \
    python -m pip install -r /OpenVid-1M/requirements.txt

# Set the PYTHONPATH to include the OpenVid repo
ENV PYTHONPATH="${PYTHONPATH}:/OpenVid-1M"

# Patch the inference script
COPY backend/models/openvid/inference.py /OpenVid-1M/scripts/inference.py

# Copy the prompt file
COPY prompts.txt /prompts.txt

# Set the entry point to activate the conda environment
ENTRYPOINT [ "conda", "run", "-n", "openvid", "/bin/bash", "-c" ]

# Default command to keep the container alive or run inference
CMD ["bash"]
