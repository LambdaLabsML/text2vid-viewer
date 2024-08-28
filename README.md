# Architecture POC

## Frontend

Displays videos using URLs fetched from the backend.
* Model centric view: preview generations by batch of 6 prompts for a given model
* Prompt centric view: preview generation by batch of 6 models for a given prompt

## Backend

## Self-hosted inference endpoints

Lambda cloud hosted inference endpoints for opensora 1.1 and 1.2
Responsible for offline, batch processing video generation based on input list of prompts

## Storage

Video generated are exported to S3 and frontend load them from there for rendering
Available video files and metadata are maintained in a small relational database

## Backend API

Endpoint to fetch available videos and metadata
(later) Endpoint for prompt submission:
video generation tasks sent to inference endpoint
files are uploaded to S3
video database gets updated


