# Text2Video Model Viewer

Visual comparison of T2V models on a set of prompts.  

Backend serves T2V models and generates video from user submitted prompts.
Frontend renders model outputs for visual comparisons:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Usage guide

1. Start a fresh GPU instance

2. Clone the repository:
```bash
git clone https://github.com/LambdaLabsML/text2vid-viewer.git
```

3. Prepare environment variables file under repo root
`/home/ubuntu/text2vid-viewer/.env`
```
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

### Run new generations

```bash
/bin/bash run_inference.sh \
    --model <opensora-v1-2> \
    --prompt-path <prompts.txt>
```

Note:
* model should have a matching config file in `backend/configs/`
* prompt file should have one prompt per line
* generation takes 3min per prompt and has additional time when loading the model for the first time; log can be seen under the inference/logs folder

### Run text2video viewer web application

```bash
/bin/bash run_frontend.sh
```



## Serve model and generate outputs




Generate video from prompts and save to S3:
```bash
curl -X POST http://209.20.156.111:5000/generate -H "Content-Type: application/json" -d '{
        "model": "lambda",
        "prompt": [
            "A video of a cat playing with a ball",
            "a beautiful waterfall",
            "a woman dancing in the rain"
            ]
    }'
```

## Frontend

Deploy frontend:
```bash
python3 -m frontend/http.server
```