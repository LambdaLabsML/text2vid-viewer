#!/bin/bash

git clone https://github.com/jy0205/Pyramid-Flow
cd Pyramid-Flow

# path inference script
cp /home/ubuntu/text2vid-viewer/backend/models/pyramidflow/inference.py /home/ubuntu/Pyramid-Flow/inference.py

# create env using conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $HOME/miniconda3 && \
    rm /tmp/miniconda.sh
export PATH="$HOME/miniconda3/bin:$PATH"
conda init
source ~/.bashrc
conda create -n pyramid python=3.8.10 -y
conda activate pyramid
pip install -r requirements.txt


python /home/ubuntu/text2vid-viewer/backend/models/pyramidflow/inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt