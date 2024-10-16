# T2V-viewer

`T2V-viewer` is a solution for visual evaluation of state-of-the-art open source text-to-video models.

Generative text-to-video models are challenging to evaluate automatically but it is easy for a human observer to determine which generated video look best between multiple options.

`T2V-viewer` was built to offer an easy way to compare model side-by-side and quickly evaluate where lies the strength and weaknesses.


**Models supported**

We are working to include the best open-source models available.
Currently `T2V-viewer` supports the following:

* OpenSora v1.2
* CogVideo
* PyramidFlow


Note: Adding a new model is easy (cf instructions to add a new model)

## Usage

**Setup**
Prepare env variable file at `/home/ubuntu/text2vid-viewer/.env`
```
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

**Inference**
```bash
/bin/bash run_inference.sh --model <model-name>
```

**frontend**
```bash
/bin/bash run_frontend.sh
```

Then, open your browser at http://<instance_IP>:8000/



 

1. Setup

Backend serves T2V models and generates video from user submitted prompts.
Frontend renders model outputs for visual comparisons:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Usage guide



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