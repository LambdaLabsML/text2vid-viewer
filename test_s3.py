import os
import boto3
import dotenv



def list_s3_bucket_items(bucket_name):
    """
    List all items in an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :return: A list of object keys in the bucket.
    """
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')

    s3_client = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

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
    dotenv.load_dotenv("/home/eole/Workspaces/text2vid-viewer/backend/inference/.env")

    print(list_s3_bucket_items("text2videoviewer"))
