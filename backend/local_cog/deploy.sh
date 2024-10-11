git clone https://github.com/THUDM/CogVideo.git
cd CogVideo
pip install -r requirements.txt

# Patch the inference script
cp /home/ubuntu/text2vid-viewer/backend/local_cog/inference.py /home/ubuntu/CogVideo/inference/inference.py

# Create log and data dir
mkdir -p /home/ubuntu/logs /home/ubuntu/data

# Run inference
python inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt \
    --save_dir /home/ubuntu/data \
    --model_path THUDM/CogVideoX-5b \
    --generate_type "t2v"