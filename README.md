# Text2Video Model Viewer

```bash
cd frontend
python3 -m http.server
```



## Frontend

Displays videos using URLs fetched from the backend.
* Model centric view: preview generations by batch of 6 prompts for a given model
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Backend

## Self-hosted inference endpoints

* Lambda cloud hosted inference endpoints; for now `opensora1.1` and `opensora1.2` with default serving config.
* Responsible for offline, batch processing video generation based on input list of prompts

## Storage

* Video generated are exported to S3 and frontend load them from there for rendering
* Available video files and metadata are maintained in a small relational database

## Backend API

* available videos and metadata
* (later) prompt submission:
  1. video generation tasks sent to inference endpoint
  2. files are uploaded to S3
  3. video database gets updated


