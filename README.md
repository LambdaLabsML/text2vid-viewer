# Text2Video Model Viewer

Visual comparison of T2V models on a set of prompts.  

Backend generates video from user submitted prompts on opensora v1.1, v1.2, and lambda-opensora models and push these videos to S3.  

Frontend renders model outputs for visual comparisons:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Backend

Deploy T2V inference endpoint:
```bash
cd backend
./remote_deploy.sh  <model_name> <hf_token>
```
with:
* `model_name`: name of the model to deploy in ('opensora-v1-1', 'opensora-v1-2', 'lambda')
* `hf_token`: huggingface token to access the model (for lambda model only)

Generate video from prompts and save to S3:
```bash
curl -X POST http://209.20.156.111:5000/generate -H "Content-Type: application/json" -d '{
        "config": "lambda.py",
        "save_dir" : "/data"
    }' --output /tmp/opensora_sample.mp4
```

## Frontend

Deploy frontend:
```bash
cd frontend
python3 -m http.server
```