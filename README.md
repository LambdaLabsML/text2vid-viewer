# t2v-eval

[t2v-eval.com](https://t2v-eval.com) is a solution to compare state-of-the-art open source text-to-video (T2V) models:
* OpenSora v1.2
* CogVideo
* PyramidFlow

*We are working to include the best open-source T2V models available.*


## Why `t2v-eval`?

The most basic way to develop a sense of the qualitative differences between t2v models is to see their outputs side-by-side and `t2v-eval` does exactly that.

It relies on many dimensions that have to do with coherence of attributes, of their relationship, of the prompt and the video output [[1](https://t2v-compbench.github.io/)]. 
A valuable way to understand the strengths and weaknesses of a model is to compare its outputs with other models on a similar task

Howeveis easy for a human observer to determine which generated video look best between multiple options.

`T2V-viewer` was built to offer an easy way to compare model side-by-side and quickly evaluate where lies the strength and weaknesses.

Two modes can be used for model evaluation:
* Model centric view: preview generations by batch of 6 prompts for a given model.
* Prompt centric view: preview generation by batch of 6 models for a given prompt


## Usage

**Setup**
Models weights are downloaded from HuggingFace and videos are stored on AWS.
Running inference and frontend assumes that a HuggingFace account and a AWS S3 bucket are setup.

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