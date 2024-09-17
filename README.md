# Text2Video Model Viewer

Visual comparison of T2V models on a set of prompts.  

Backend generates video from user submitted prompts on opensora v1.1, v1.2, and lambda-opensora models and push these videos to S3.  

Frontend renders model outputs for visual comparisons:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Backend

Prepare `.env` file:
```bash
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_DEFAULT_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

Deploy T2V inference endpoint:
```bash
cd backend/inference
./remote_deploy.sh  <model_name>
```
with:
* `model_name`: name of the model to deploy in ('opensora-v1-1', 'opensora-v1-2', 'lambda')

Generate video from prompts and save to S3:
```bash
curl -X POST http://209.20.156.111:5000/generate -H "Content-Type: application/json" -d '{
        "config": "lambda.py",
        "prompt": "A video of a cat playing with a ball" "a beautiful waterfall" "a woman dancing in the rain",
    }'
```

## Frontend

Deploy frontend:
```bash
cd frontend
python3 -m http.server
```