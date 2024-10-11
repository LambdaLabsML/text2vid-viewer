sudo docker run \
    --gpus all \
    -v /home/ubuntu/data:/data \
    openvid-image \
        torchrun \
            --standalone \
            --nproc_per_node 1 \
            scripts/inference.py \
            --config configs/stdit/inference/16x1024x1024.py \
            --ckpt-path STDiT-16x1024x1024.pt \
            --prompt-path /data/prompts.txt \
            --save-dir /data