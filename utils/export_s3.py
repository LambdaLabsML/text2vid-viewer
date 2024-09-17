"""
export AWS_ACCESS_KEY_ID=<>
export AWS_SECRET_ACCESS_KEY=<>
export AWS_DEFAULT_REGION=us-east-1
"""

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

load_dotenv("../backend/inference/.env")

def upload_file_to_s3(file_name, bucket_name, object_name, metadata):
    """
    Uploads a file to an S3 bucket.

    :param file_name: Path to the file to upload.
    :param bucket_name: Name of the S3 bucket.
    :param object_name: S3 object name. If not specified, file_name is used.
    :return: The S3 object name if the file was uploaded successfully, else None.
    """

    # Create an S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
        aws_secret_access_key=os.environ["AWS_SECRET_KEY"])

    try:
        # Upload the file
        s3_client.upload_file(file_name, bucket_name, object_name, ExtraArgs={'Metadata': metadata})
        print(f"File {file_name} uploaded to {bucket_name}/{object_name}.")
        return object_name
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


import boto3

def list_s3_bucket_items(bucket_name):
    """
    List all items in an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :return: A list of object keys in the bucket.
    """
    # Create an S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
        aws_secret_access_key=os.environ["AWS_SECRET_KEY"])

    # List to store all object keys
    object_keys = []

    try:
        # Pagination to handle large number of objects
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    object_keys.append(obj['Key'])
                    print(obj['Key'])  # Print each object's key

    except Exception as e:
        print(f"An error occurred: {e}")

    return object_keys



if __name__ == "__main__":
        
    # import os
    # bucket_name = "text2videoviewer"
    # video_base_path = "/home/eole/Desktop/lambda-opensora"
    # model = "lambda-stdit-720"
    # prompt_fpath = "/home/eole/Workspaces/text2vid-viewer/backend/inference/prompts.txt"

    # with open(prompt_fpath, "r") as f:
    #     prompts = [l.strip() for l in f.readlines()]
    #     video_fnames =  os.listdir(video_base_path)
    #     video_fnames.sort()

    # for video_fname, prompt in zip(video_fnames, prompts):
    #     video_fpath = f"{video_base_path}/{video_fname}"
    #     object_name = f"{model}/{prompt}.mp4"
    #     metadata = {
    #         "model": model,
    #         "prompt": prompt
    #     }
    #     print(f"Model: {model}")
    #     print(f"Prompt: {prompt}")
    #     print(f"Video path: {video_fpath}")
    #     print(f"Object name: {object_name}")
            
    #     response = upload_file_to_s3(video_fpath, bucket_name, object_name, metadata)
    #     if response is not None:
    #         print("File uploaded successfully.")
    #     else:
    #         print("File uploaded failed.")
    #     print()

    # -------------------------------
    bucket_name = 'text2videoviewer'
    all_objects = list_s3_bucket_items(bucket_name)
    print(all_objects)

    records = []
    for obj in all_objects:
        model = obj.split("/")[0]
        prompt = obj.split("/")[1].split(".")[0]
        print(model, prompt)
        records.append({"model": model, "prompt": prompt, "object_name": obj})
    # Save as CSV
    import pandas as pd
    df = pd.DataFrame(records)
    df.to_csv("upload_records.csv", index=False)











    # -------------------------------


    # models = [
    #     "sora1.2-stdit-720p",
    #     "sora1.2-stdit-480p",
    #     "sora1.1-stdit-480p"
    # ]

    # # PROMPTS
    # with open(os.path.join(fpath, "prompts.txt"), "r") as f:
    #     prompts = [l.strip() for l in f.readlines()]


    # # UPLOAD
    # records  = []
    # for model in models:
    #     print(model)
    #     print("\n")

    #     video_fnames =  os.listdir(f"{fpath}/{model}")
    #     video_fnames.sort()

    #     for prompt_i, prompt in enumerate(prompts):
    #         video_fname = video_fnames[prompt_i]
    #         video_fpath = f"{fpath}/{model}/{video_fname}"
    #         object_name = f"{model}/{prompt}.mp4"
    #         metadata = {
    #             "model": model,
    #             "prompt": prompt
    #         }
    #         print(f"Model: {model}")
    #         print(f"Prompt: {prompt}")
    #         print(f"Video path: {video_fpath}")
    #         print(f"Object name: {object_name}")


    #         response = upload_file_to_s3(video_fpath, bucket_name, object_name, metadata)
    #         if response is not None:
    #             print("File uploaded successfully.")

    #         else:
    #             records.append({"model": model, "prompt": prompt, "object_name": object_name})
    # # Save as CSV
    # import pandas as pd
    # df = pd.DataFrame(records)
    # df.to_csv("upload_records.csv", index=False)

    # Example usage
    # bucket_name = 'text2videoviewer'
    # all_objects = list_s3_bucket_items(bucket_name)
    # print(all_objects)

    # records = []
    # for obj in all_objects:
    #     model = obj.split("/")[0]
    #     prompt = obj.split("/")[1].split(".")[0]
    #     print(model, prompt)
    #     records.append({"model": model, "prompt": prompt, "object_name": obj})
    # # Save as CSV
    # import pandas as pd
    # df = pd.DataFrame(records)
    # df.to_csv("upload_records.csv", index=False)

    






        