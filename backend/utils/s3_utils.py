import pandas as pd
import csv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

def upload_file_to_s3(file_name, bucket_name, object_name, metadata={}):
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
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

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


def list_s3_bucket_items(bucket_name):
    """
    List all items in an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :return: A list of object keys in the bucket.
    """
    # Create an S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

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
                    #print(obj['Key'])  # Print each object's key

    except Exception as e:
        print(f"An error occurred: {e}")

    return object_keys


def update_csv(csv_fpath, bucket_name="text2videoviewer"):
    all_objects = list_s3_bucket_items(bucket_name)
    records = []
    for obj in all_objects:
        # Split the object name into model and the rest
        parts = obj.split("/", 1)
        if len(parts) != 2:
            continue  # Skip if the object name doesn't match expected pattern
        model = parts[0]
        filename = parts[1]

        # Remove the file extension to get the prompt
        prompt = filename.rsplit(".", 1)[0]
        prompt = prompt.strip().strip('"').strip("'").strip('\n').strip()

        # No longer removing commas from prompts
        records.append({"model": model, "prompt": prompt, "object_name": obj})

    # Save as CSV with proper quoting
    df = pd.DataFrame(records)
    df.to_csv(csv_fpath, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')


import boto3
import os

def clean_prompt(prompt):
    """
    Cleans up the prompt by stripping leading/trailing newlines or quotation marks.
    
    :param prompt: The prompt string.
    :return: The cleaned prompt string.
    """
    if prompt.startswith(r'\ n'):
        prompt = prompt[3:]
    # remove comma anywhere in prompt
    prompt = prompt.replace(",", "")
    prompt = prompt.replace("'", "")
    return prompt.strip().strip('"').strip("'")

def rename_s3_objects(bucket_name):
    """
    Renames all objects in the specified S3 bucket to ensure the 'prompt' part 
    of the key does not contain trailing or leading newline characters or 
    quotation marks.
    
    :param bucket_name: Name of the S3 bucket.
    """

    # Initialize S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    # List all objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' not in response:
        print(f"No objects found in bucket {bucket_name}.")
        return

    for obj in response['Contents']:
        old_key = obj['Key']
        
        # Assuming object keys follow the format <bucket-name>/<model-name>/prompt
        parts = old_key.split('/')
        if len(parts) < 2:
            print(f"Skipping object with key: {old_key}. Invalid format.")
            continue
        
        # Clean the prompt part of the key
        model_name = parts[0]
        prompt = parts[1]
        cleaned_prompt = clean_prompt(prompt)
        
        if cleaned_prompt != prompt:
            # Create the new object key
            new_key = f"{model_name}/{cleaned_prompt}"
            
            # Copy the object to the new key
            #s3_client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': old_key}, Key=new_key)
            
            # Check if new key exists
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            if new_key in [obj['Key'] for obj in response['Contents']]:
                s3_client.delete_object(Bucket=bucket_name, Key=old_key)

            else:
                print(f"Need to rename {old_key} to {new_key}.")
                response = input(f"ok? (y/n): ", default='y')
            
            #print(f"Renamed {old_key} to {new_key}.")
        else:
            print(f"No renaming needed for {old_key}.")



def list_model_prompts_in_s3(bucket_name, model_name):
    """
    List all prompts for a specific model in the S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param model_name: Name of the model to filter objects by.
    :return: A list of prompts for the model.
    """
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    # List to store the prompts
    prompts = []

    # List all objects in the bucket
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=model_name)

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                prompt = obj['Key'].split("/")[1].split(".")[0]
                prompt = prompt.strip().strip('"').strip("'").strip('\n')
                prompts.append(prompt)

    return prompts

def compare_prompts(bucket_name, model_a, model_b):
    """
    Compares the prompts in two models and returns the differences.
    
    :param bucket_name: S3 bucket name.
    :param model_a: Name of the first model.
    :param model_b: Name of the second model.
    :return: Two lists of prompts. One not in Model A and one not in Model B.
    """
    # Get prompts from both models
    prompts_a = set(list_model_prompts_in_s3(bucket_name, model_a))
    prompts_b = set(list_model_prompts_in_s3(bucket_name, model_b))

    # Find prompts that are not in each model
    prompts_not_in_a = list(prompts_b - prompts_a)
    prompts_not_in_b = list(prompts_a - prompts_b)

    print("Prompt in", model_a, "but not in", model_b, ":\n")
    for p in prompts_not_in_b:
        print(p)

    print("\n")
    print("Prompt in", model_b, "but not in", model_a, ":\n")
    print()
    for p in prompts_not_in_a:
        print(p)



if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv(".env")

    bucket_name = "text2videoviewer"
    rename_s3_objects(bucket_name)
    #compare_prompts(bucket_name, "cog", "opensora-v1-2-240p")

    #---------------------------
        
    # import os
    # bucket_name = "text2videoviewer"
    # video_base_path = "/home/eole/Desktop/lambda-opensora-speedrun"
    # model = "lambda-speedrun"
    # prompt_fpath = "/home/eole/Workspaces/text2vid-viewer/backend/prompts.txt"

    # with open(prompt_fpath, "r") as f:
    #     prompts = [l.strip() for l in f.readlines()]
    #     video_fnames =  os.listdir(video_base_path)
    #     video_fnames.sort()
    #     #prompts = [p for p in prompts if p != "close up shot of a yellow taxi turning left"] 

    # assert len(prompts) == len(video_fnames), "Number of prompts and videos do not match."

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
    #     print()
            
    #     response = upload_file_to_s3(video_fpath, bucket_name, object_name, metadata)
    #     if response is not None:
    #         print("File uploaded successfully.")
    #     else:
    #         print("File uploaded failed.")
    #     print()

    # -------------------------------
    
    #update_csv(csv_fpath="/home/eole/Workspaces/text2vid-viewer/frontend/db.csv")

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

    






        