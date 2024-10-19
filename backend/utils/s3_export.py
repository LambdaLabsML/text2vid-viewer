import argparse
import os
import logging
import glob
from s3_utils import upload_file_to_s3
from dotenv import load_dotenv

if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv("/home/ubuntu/text2vid-viewer/.env")
     
    # Parse `model` argument
    parser = argparse.ArgumentParser(description="Send generated videos to S3")
    parser.add_argument("--model", type=str, required=True, help="Name of the model configuration to use")
    parser.add_argument("--prompt_csv", type=str, required=False, help="Path to the prompt csv file")
    
    args = parser.parse_args()
    model = args.model
    prompt_csv = args.prompt_csv

    # If exists read prompt csv to get prompt -> prompt_base mapping
    prompt_base_mapping = {}
    if prompt_csv and os.path.exists(prompt_csv):
        import pandas as pd
        df = pd.read_csv(prompt_csv)
        prompt_base_mapping = dict(zip(df['prompt'], df['prompt_base']))

    # Export to S3
    generated_files = glob.glob(os.path.join("/home/ubuntu/data", '*.mp4'))
    for generated_file_path in generated_files:
        prompt = os.path.basename(generated_file_path).split('.mp4')[0]
        prompt_base = prompt_base_mapping.get(prompt, None)
        bucket_name = "text2videoviewer"
        object_name = f"{model}/{prompt}.mp4"

        metadata = {
            "model": model,
            "prompt": prompt,
            "prompt_base" : prompt_base
        }

        response = upload_file_to_s3(generated_file_path, bucket_name, object_name, metadata)
        if response is not None:
            print(f"File {generated_file_path} uploaded successfully as {response}.")
            os.remove(generated_file_path)
            print(f"Removed file after sending: {generated_file_path}")
        else:
            print(f"File upload failed for {generated_file_path}.")