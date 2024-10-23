cd /home/ubuntu
git clone https://github.com/genmoai/models
cd models 
pip install uv

uv venv .venv
source .venv/bin/activate

uv pip install -e . --no-build-isolation


pip install -r requirements.txt
pip install huggingface_hub[cli]

# Download model weights
python /home/ubuntu/text2vid-viewer/backend/models/mochi/dl_weights.py

# Patch the inference script
cp /home/ubuntu/text2vid-viewer/backend/models/cog/inference.py /home/ubuntu/CogVideo/inference/inference.py

# Run inference
python /home/ubuntu/CogVideo/inference/inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt \
    --save_dir /home/ubuntu/data/cog \
    --model_path THUDM/CogVideoX-5b \
    --generate_type "t2v"