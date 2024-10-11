# Text2Video Model Viewer

Visual comparison of T2V models on a set of prompts.  

1. Setup

Backend serves T2V models and generates video from user submitted prompts.
Frontend renders model outputs for visual comparisons:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Usage guide

### Run inference

1. Clone the repository:
```bash
git clone https://github.com/LambdaLabsML/text2vid-viewer.git
```

2. Prepare env variable file : `/home/ubuntu/text2vid-viewer/.env`
```
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

4. Prepare prompt file: `/home/ubuntu/text2vid-viewer/prompts.txt`

For example:
```
echo "A cat playing with a ball" > /home/ubuntu/text2vid-viewer/prompts.txt
```
Note: prompt file should have one prompt per line

5. Prepare model config `/home/ubuntu/text2vid-viewer/backend/models/opensora/configs/<base-model>-<resolution>.py`

6. Run inference
```bash
/bin/bash run_inference.sh --model <opensora-v1-2-720p>
```

Note:
* model should have a matching config file in `backend/models/opensora/configs/`
* inference logs are piped to /home/ubuntu/logs/inference.log
* outputs are directly exported to S3

### Run web application (frontend)

1. Clone the repository not already done
```bash
git clone https://github.com/LambdaLabsML/text2vid-viewer.git
```

2. Run the frontend
```bash
python3 text2vid-viewer/run_frontend.sh
```
Note: http://<instance_IP>:8000/ to access the frontend