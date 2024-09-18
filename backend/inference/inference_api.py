from flask import Flask, request, jsonify
import subprocess
import os
import logging
import glob
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)

# Configure logging to file
logging.basicConfig(filename='/app/logs/inference_api.log', 
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def get_cmd_list(config_file, save_dir="/data"):
    """Prepare the command list for image generation."""
    cmd = [
        'python', 'scripts/inference.py',
        config_file,
        '--save-dir', save_dir,
        '--prompt-path', os.path.join(save_dir, 'prompts.txt'),
        '--prompt-as-path']

    logging.debug(f"Running command: {' '.join(cmd)}")
    return cmd

@app.route('/generate', methods=['POST'])
def generate_image():

    import os

    try:
        data = request.json
        logging.debug(f"Request data: {data}")

        # Remove files with name pattern `sample_*.mp4`
        save_dir = os.environ.get('SAVE_DIR', '/data')
        for file_path in glob.glob(os.path.join(save_dir, '*.mp4')):
            os.remove(file_path)
            logging.debug(f"Removed file: {file_path}")

        # Determine config file
        config_files = os.listdir('/app/custom_configs/')
        config_models = [config_name[:-3] for config_name in config_files]

        model = data.get('model', 'opensora-v1-2')
        if model not in config_models:
            raise ValueError(f"Invalid model: {model}; should be in {' '.join(config_models)}")
        config_file = f'/app/custom_configs/{model}.py'

        prompts = data.get('prompt', 'a beautiful waterfall')
        if not isinstance(prompts, list):
            prompts = [prompts]

        # Save prompts to text file
        prompts_file = os.path.join(save_dir, 'prompts.txt')
        with open(prompts_file, 'w') as f:
            for prompt in prompts:
                f.write(prompt + '\n')

        # Run inference cmd with all prompts
        cmd_list = get_cmd_list(config_file)
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        logging.debug(f"Command output: {result.stdout}")  
        logging.error(f"Command error output: {result.stderr}")

        responses = []

        if result.returncode == 0:

            generated_files = glob.glob(os.path.join(save_dir, '*.mp4'))
            for generated_file_path in generated_files:
                prompt = os.path.basename(generated_file_path).split('.mp4')[0]
                bucket_name = "text2videoviewer"
                object_name = f"{model}/{prompt}.mp4"
                metadata = None
                response = upload_file_to_s3(generated_file_path, bucket_name, object_name, metadata)

                if response is not None:
                    logging.debug(f"File {generated_file_path} uploaded successfully as {response}.")
                    responses.append({'prompt': prompt, 's3_path': response})

                    os.remove(generated_file_path)
                    logging.debug(f"Removed file after sending: {generated_file_path}")
                else:
                    logging.error(f"File upload failed for {generated_file_path}.")
                    responses.append({'prompt': prompt, 'error': 'File upload failed'})

                return jsonify(responses), 200
        else:
            logging.error(f"Image generation failed")
            return jsonify({'message': 'Image generation failed', 'error': result.stderr}), 500

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500


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
    aws_region = os.getenv('AWS_REGION')

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
        logging.debug(f"File {file_name} uploaded to {bucket_name}/{object_name}.")
        return object_name
    except FileNotFoundError:
        logging.debug(f"The file {file_name} was not found.")
        return None
    except NoCredentialsError:
        logging.debug("Credentials not available.")
        return None
    except PartialCredentialsError:
        logging.debug("Incomplete credentials provided.")
        return None
    except Exception as e:
        logging.debug(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    logger.info("Starting the inference API server")
    app.run(host='0.0.0.0', port=5000, debug=False)
