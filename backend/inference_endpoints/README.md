# Deploying OpenSora 1.2 for inference on Lambda On-demand Cloud instances

Requirements:
* Build `opensora` or `opensora_api` image (see steps below)
* Create `~/data` dir to mount to the opensora container (should be included in the setup for step#1)

Notes:
* sora1.2 max res is 720p and sora1.1 max res is 480p

## Simple workflow, directly run in ODC node


Start the container in detached mode and keep it running:
```bash
sudo docker run -d --gpus all -v /home/ubuntu/data:/data --name opensora_container opensora_api:latest tail -f /dev/null
```

Execute the command in the running container:
```bash
sudo docker exec opensora_container nohup python scripts/inference.py \
    configs/opensora-v1-2/inference/sample.py \
    --num-frames 96 \
    --resolution 720p \
    --aspect-ratio 9:16 \
    --prompt-path /data/sample_prompts.txt \
    --save-dir /data/sora1.2 > /home/ubuntu/data/opensora.log 2>&1 &
```

Note:
* Command ran with `nohup` so terminal can be closed without interruting run
* Use `sudo docker stop opensora_container` to stop running container and interrupt job
* Use `sudo docker rm opensora_container` to remove container
* logs are being written to `/home/ubuntu/data/opensora.log`

### Interactive mode (debug)

Run container in interactive mode:
```bash
mkdir home/ubuntu/data
sudo docker run -ti --gpus all -v /home/ubuntu/data:/data opensora_api:latest
```

Run inference in container:
```bash
(pytorch) root@6a7431d9eadb:/workspace/Open-Sora# 
python scripts/inference.py \
    configs/opensora-v1-2/inference/sample.py \
    --num-frames 4s \
    --resolution 360p \
    --aspect-ratio 9:16 \
    --prompt "a beautiful waterfall" \
    --save-dir /data
```

Multiple generation
```bash
python scripts/inference.py \
    configs/opensora-v1-2/inference/sample.py \
    --num-frames 96 \
    --resolution 360p \
    --aspect-ratio 9:16 \
    --prompt "a beautiful waterfall" "a young woman dancing" \
    --save-dir /data
```

Generation from prompts file
```bash
python scripts/inference.py \
    configs/opensora-v1-2/inference/sample.py \
    --num-frames 96 \
    --resolution 720p \
    --aspect-ratio 9:16 \
    --prompt-path /data/sample_prompts.txt \
    --save-dir /data/sora1.2
```

---


## Endpoint workflow (WIP)

### Setup remote endpoint (script)

The following assumes ssh access to a lambda ODC instance.

```bash
cd ~/Workspaces/image-eval/models/opensora && chmod +x remote_deploy.sh
```

```bash
./remote_deploy.sh
```


### Setup remote endpoint (manual step-by-step)

Build opensora base image
```bash
git clone https://github.com/hpcaitech/Open-Sora.git
cd Open-Sora
sudo docker build -t opensora -f Dockerfile .
```

Clone this repo if you haven't already:
```bash
cd ~
git clone https://github.com/LambdaLabsML/image-eval.git
```

Build opensora inference server image
```bash
cd image-eval/models/opensora
sudo docker build -t opensora_api  .
```

Run the inference server
```bash
sudo docker run -d --gpus all -p 5000:5000 -v /home/ubuntu/data:/data opensora_api:latest
```

To shut down the running container
```bash
sudo docker ps # identify name of container to stop
sudo docker stop <container_name> # stop container
```

Remove image and stop container:
```bash
sudo docker ps # identify name of container to stop
sudo docker stop <container_name> # stop container
sudo docker rmi opensora_api:latest

```

## Usage

Make request to the inference server:
```bash
export SERVER_IP=140.238.37.247
curl -X POST http://${SERVER_IP}:5000/generate -H "Content-Type: application/json" -d '{
    "num_frames": "24",
    "resolution": "360p",
    "aspect_ratio": "16:9",
    "prompt": "a beautiful sunset",
    "save_dir" : "/data"
}' --output /tmp/opensora_sample.mp4
```




---


Notes:
* source: https://github.com/hpcaitech/Open-Sora?tab=readme-ov-file#inference
* Ran into issues with non docker route stemming from different CUDA version in ODC and in the OpenSora docs. For instance, xformers was not compatible with the CUDA version in the ODC. Tried building from source to no avail.
* Needed to use `sudo` with docker because I ran into permission issue using docker on ODC otherwise