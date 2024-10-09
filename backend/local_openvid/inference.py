import argparse
import subprocess
import os
import logging
import glob
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure logging to file
logging.basicConfig(filename='/app/logs/inference.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def get_cmd_list():
    """Prepare the command list for video generation."""
    cmd = [
        'torchrun', '--standalone', '--nproc_per_node', '1',
        'scripts/inference.py',
        '--config', 'configs/stdit/inference/16x1024x1024.py',
        '--ckpt-path', 'STDiT-16x1024x1024.pt',
        '--prompt-path', '/app/prompts.txt',
        '--save-dir', '/data'
    ]

    logger.debug(f"Running command: {' '.join(cmd)}")
    return cmd


def upload_file_to_s3(file_name, bucket_name, object_name, metadata):
    """
    Uploads a file to an S3 bucket.

    :param file_name: Path to the file to upload.
    :param bucket_name: Name of the S3 bucket.
    :param object_name: S3 object name.
    :return: The S3 object name if the file was uploaded successfully, else None.
    """

    # Create an S3 client
    # Get AWS credentials from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')

    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        # Prepare ExtraArgs
        extra_args = {}
        if metadata is not None:
            extra_args['Metadata'] = metadata

        # Upload the file
        s3_client.upload_file(file_name, bucket_name, object_name, ExtraArgs=extra_args)
        logger.debug(f"File {file_name} uploaded to {bucket_name}/{object_name}.")
        return object_name
    except FileNotFoundError:
        logger.debug(f"The file {file_name} was not found.")
        return None
    except NoCredentialsError:
        logger.debug("Credentials not available.")
        return None
    except PartialCredentialsError:
        logger.debug("Incomplete credentials provided.")
        return None
    except Exception as e:
        logger.debug(f"An error occurred: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Inference script for OpenVid-1M")
    parser.add_argument('--model', type=str, required=False, help='(Unused) Name of the model configuration to use')
    args = parser.parse_args()

    # Remove punctuation from prompts
    logger.debug("Removing punctuation from prompts")
    with open("/app/prompts.txt", "r") as f:
        prompts = f.readlines()

    prompts = [prompt.replace(",", "").replace(".", "").replace("!", "").strip() for prompt in prompts]
    with open("/app/prompts.txt", "w") as f:
        for prompt in prompts:
            f.write(prompt + "\n")

    # Remove existing mp4 files in the save directory
    for file_path in glob.glob(os.path.join("/data", '*.mp4')):
        os.remove(file_path)
        logger.debug(f"Removed file: {file_path}")

    # Run inference
    cmd_list = get_cmd_list()
    result = subprocess.run(cmd_list, capture_output=True, text=True, cwd="/app/OpenVid-1M")
    logger.debug(f"Command output: {result.stdout}")
    logger.error(f"Command error output: {result.stderr}")

    # Check if error occurred
    if result.returncode != 0:
        logger.error("Video generation failed")
        return

    # Export to S3
    generated_files = glob.glob(os.path.join("/data", '*.mp4'))
    for generated_file_path in generated_files:
        prompt = os.path.basename(generated_file_path).split('.mp4')[0]
        bucket_name = os.getenv('S3_BUCKET_NAME', 'text2videoviewer')
        object_name = f"{prompt}.mp4"
        metadata = None
        response = upload_file_to_s3(generated_file_path, bucket_name, object_name, metadata)

        if response is not None:
            logger.debug(f"File {generated_file_path} uploaded successfully as {response}.")
            os.remove(generated_file_path)
            logger.debug(f"Removed file after sending: {generated_file_path}")
        else:
            logger.error(f"File upload failed for {generated_file_path}.")


if __name__ == '__main__':
    logger.info("\n\n")
    logger.info("Starting the inference process")
    main()
