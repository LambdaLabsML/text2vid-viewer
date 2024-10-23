cd /home/ubuntu
git clone https://github.com/genmoai/models mochi
cd mochi 
pip install uv

uv venv .venv
source .venv/bin/activate
uv pip install -e . --no-build-isolation
.venv/bin/python3 -m pip install -r requirements.txt
.venv/bin/python3 -m pip install huggingface_hub[cli]

# Patch the inference script
cp /home/ubuntu/text2vid-viewer/backend/models/mochi/inference.py /home/ubuntu/mochi/src/mochi_preview/inference.py

# Download model weights
.venv/bin/python3 /home/ubuntu/text2vid-viewer/backend/models/mochi/dl_weights.py


# Run inference
.venv/bin/python3 /home/ubuntu/mochi/src/mochi_preview/inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt \
    --save_dir /home/ubuntu/data/mochi \
    --model_path THUDM/CogVideoX-5b