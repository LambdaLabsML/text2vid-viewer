import csv
import pandas as pd
import boto3
from s3_utils import list_s3_bucket_items
#from s3_utils import update_csv


# Function to get metadata from an S3 object
def get_s3_object_metadata(bucket_name, object_name):
    s3_client = boto3.client("s3")
    response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
    return response["Metadata"]

# Function to update CSV with metadata fields
def update_csv(csv_fpath, bucket_name="text2videoviewer"):
    all_objects = list_s3_bucket_items(bucket_name)
    records = []
    
    for obj in all_objects:
        # Get the metadata for each object
        metadata = get_s3_object_metadata(bucket_name, obj)

        # Check if the expected metadata keys exist
        model = metadata.get("model", "unknown_model")
        prompt = metadata.get("prompt", "unknown_prompt")
        base_prompt = metadata.get("base_prompt", "unknown_base_prompt")

        records.append({
            "model": model, 
            "prompt": prompt, 
            "base_prompt": base_prompt, 
            "object_name": obj
        })

    # Create DataFrame
    df = pd.DataFrame(records)
    print(f"Found a total of {len(records)} videos in S3.")

    # Filter models
    df = filter_records_based_on_model(df)

    # Filter prompts based on prompts.csv
    df = filter_records_based_on_prompts(df, "prompts.csv")

    # Print number of prompts filtered out and number of prompts kept
    print(f"Kept {len(df)} videos.")

    # Update name "opensora" to "opensora-v1.2"
    df["model"] = df["model"].replace({"opensora": "opensora-v1.2"})

    df.to_csv(csv_fpath, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')


# Function to filter DataFrame based on records in prompts.csv
def filter_records_based_on_prompts(df, prompts_csv_fpath):
    prompts_df = pd.read_csv(prompts_csv_fpath)
    filtered_df = df[df["prompt"].isin(prompts_df["prompt"])]

    # Print information about kept and excluded prompts
    for model in filtered_df["model"].unique():
        print(f"Kept prompts for model {model} ({len(filtered_df[filtered_df['model'] == model]['prompt'].unique())} videos):")
        for prompt in filtered_df[filtered_df["model"] == model]["prompt"].unique():
            print(f"\t{prompt}")
        
        excluded_prompts = set(prompts_df["prompt"]) - set(filtered_df[filtered_df["model"] == model]["prompt"].unique())
        print(f"Excluded prompts for model {model} ({len(excluded_prompts)} prompts):")
        for prompt in excluded_prompts:
            print(f"\t{prompt}")
    
    return filtered_df

# Function to filter DataFrame based on model
def filter_records_based_on_model(df, sota_models=["cog", "pyramidflow", "opensora"]):
    filtered_df = df[df["model"].isin(sota_models)]
    
    # Print filtering result for models
    print(f"Filtered to {len(filtered_df)} records from the following SOTA models: {', '.join(sota_models)}.")
    
    return filtered_df



def refresh_db():

    # csv_fpath is located in the parent of the script's parent directory
    csv_fpath = "/home/ubuntu/text2vid-viewer/frontend/db.csv"

    # Call the function with the dynamically constructed path as a string
    update_csv(csv_fpath=str(csv_fpath))

if __name__ == "__main__":

    refresh_db()
