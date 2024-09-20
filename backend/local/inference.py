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


def get_cmd_list(config_file):
    """Prepare the command list for image generation."""
    cmd = [
        'python', 'scripts/inference.py', config_file,
        '--save-dir', "/data",
        '--prompt-path', "/app/prompts.txt",
        '--prompt-as-path']

    logger.debug(f"Running command: {' '.join(cmd)}")
    return cmd


def upload_file_to_s3(file_name, bucket_name, object_name, metadata):
    """
    Uploads a file to an S3 bucket.

    :param file_name: Path to the file to upload.
    :param bucket_name: Name of the S3 bucket.
    :param object_name: S3 object name. If not specified, file_name is used.
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
    parser = argparse.ArgumentParser(description="Inference script for OpenSora")
    parser.add_argument('--model', type=str, required=True, help='Name of the model configuration to use')
    args = parser.parse_args()

    try:
        # Remove existing files with the pattern `*.mp4` in the save directory
        for file_path in glob.glob(os.path.join("/data", '*.mp4')):
            os.remove(file_path)
            logger.debug(f"Removed file: {file_path}")

        # Determine config file
        config_file = f'/app/custom_configs/{args.model}.py'
        if not os.path.exists(config_file):
            raise ValueError(f"Config file for model {args.model} does not exist: {config_file}")

        # Run inference command with the provided prompt path
        cmd_list = get_cmd_list(config_file)
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        logger.debug(f"Command output: {result.stdout}")
        logger.error(f"Command error output: {result.stderr}")

        if result.returncode == 0:
            generated_files = glob.glob(os.path.join("/data", '*.mp4'))
            for generated_file_path in generated_files:
                prompt = os.path.basename(generated_file_path).split('.mp4')[0]
                bucket_name = "text2videoviewer"
                object_name = f"{args.model}/{prompt}.mp4"
                metadata = None
                response = upload_file_to_s3(generated_file_path, bucket_name, object_name, metadata)

                if response is not None:
                    logger.debug(f"File {generated_file_path} uploaded successfully as {response}.")
                    os.remove(generated_file_path)
                    logger.debug(f"Removed file after sending: {generated_file_path}")
                else:
                    logger.error(f"File upload failed for {generated_file_path}.")
        else:
            logger.error("Image generation failed")

    except Exception as e:
        logger.exception("An unexpected error occurred")


if __name__ == '__main__':

    # Check script/inference.py exists
    import os
    if not os.path.exists('scripts/inference.py'):
        logger.error("The script 'scripts/inference.py' does not exist.")

    logger.info("\n\n")
    logger.info("Starting the inference process")
    main()
