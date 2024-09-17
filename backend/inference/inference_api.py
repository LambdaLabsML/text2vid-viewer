from flask import Flask, request, jsonify, send_file
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


def get_cmd_list(config_file, prompts=["a beautiful waterfall"], save_dir="/data"):
    """Prepare the command list for image generation."""
    cmd = [
        'python', 'scripts/inference.py',
        config_file,
        '--prompt'
    ] + prompts + ['--save-dir', save_dir]
    logging.debug(f"Running command: {' '.join(cmd)}")
    return cmd

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.json
        logging.debug(f"Request data: {data}")

        # Remove files with name pattern `sample_*.mp4`
        save_dir = os.environ.get('SAVE_DIR', '/data')
        for file_path in glob.glob(os.path.join(save_dir, 'sample_*.mp4')):
            os.remove(file_path)
            logging.debug(f"Removed file: {file_path}")

        # Determine config file
        model = data.get('model', 'opensora-v1-2')
        if model not in ['lambda', 'opensora-v1-1', 'opensora-v1-2']:
            raise ValueError(f"Invalid model: {model}; should be in ['lambda', 'opensora-v1-1', 'opensora-v1-2']")
        config_file = f'/app/custom_configs/{model}.py'

        prompts = data.get('prompt', 'a beautiful waterfall')
        if not isinstance(prompts, list):
            prompts = [prompts]

        # Run inference cmd with all prompts
        cmd_list = get_cmd_list(config_file, prompts, save_dir)
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        logging.debug(f"Command output: {result.stdout}")  
        logging.error(f"Command error output: {result.stderr}")

        responses = []

        if result.returncode == 0:
            # Get the list of generated files
            generated_files = sorted(glob.glob(os.path.join(save_dir, 'sample_*.mp4')))
            if len(generated_files) != len(prompts):
                logging.error(f"Number of generated files ({len(generated_files)}) does not match number of prompts ({len(prompts)})")
                return jsonify({'message': 'Mismatch in number of generated files and prompts'}), 500

            for prompt, generated_file_path in zip(prompts, generated_files):
                if os.path.exists(generated_file_path):
                    bucket_name = "text2videoviewer"

                    model_fullname = None
                    if model == 'lambda':
                        model_fullname = 'lambda-stdit-720p'
                    elif model == 'opensora-v1-1':
                        model_fullname = 'sora1.1-stdit-480p'
                    elif model == 'opensora-v1-2':
                        model_fullname = 'sora1.2-stdit-720p'

                    object_name = f"{model_fullname}/{prompt}.mp4"
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


                else:
                    logging.error(f"Generated file not found: {generated_file_path}")
                    responses.append({'prompt': prompt, 'error': 'File not found'})

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
    s3_client = boto3.client('s3')

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
