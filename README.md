# Text2Video Model Viewer

Visual comparison of T2V models on a set of prompts.  

Backend serves T2V models and generates video from user submitted prompts.
Frontend renders model outputs for visual comparisons:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Serve model and generate outputs

Prepare `.env` file:
```bash
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

Deploy T2V inference endpoint:
```bash
cd backend/inference
./run.sh
```

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