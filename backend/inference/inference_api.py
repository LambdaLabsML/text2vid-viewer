from flask import Flask, request, jsonify, send_file
import subprocess
import os
import logging
import glob

app = Flask(__name__)

# Configure logging to file
logging.basicConfig(filename='/data/api_server.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def get_cmd_list(data):
    """Prepare the command list for image generation."""

    config = data.get('config', 'opensora-v1-2.py')
    if config not in ['lambda.py', 'opensora-v1-1.py', 'opensora-v1-2.py']:
        raise ValueError(f"Invalid config: {config}; should be in ['lambda.py', 'opensora-v1-1.py', 'opensora-v1-2.py']")
    config_file = f'/workspace/Open-Sora/custom_configs/{config}'

    cmd = [
        'python', 'scripts/inference.py',
        config_file,
        '--prompt', data.get('prompt', 'a beautiful waterfall'),
        '--save-dir', os.environ.get('SAVE_DIR', '/data')
    ]

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

        # Run inference cmd
        cmd_list = get_cmd_list(data)
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        logging.debug(f"Command output: {result.stdout}")  
        logging.error(f"Command error output: {result.stderr}")
        
        if result.returncode == 0:
            # Assuming the generated file is saved in the save_dir with a known name
            generated_file_path = os.path.join(save_dir, 'sample_0000.mp4')  # Update this with the correct filename
            if os.path.exists(generated_file_path):
                
                bucket_name = "text2videoviewer"
                video_fpath = generated_file_path
                object_name = f"{data.get('model', 'sora1.2-stdit-720p')}/{data.get('prompt', 'a beautiful waterfall')}.mp4"
                metadata = None
                response = upload_file_to_s3(video_fpath, bucket_name, object_name, metadata)
                # response = send_file(generated_file_path, as_attachment=True)
                
                # Confirm file sent to S3
                if response is not None:
                    logging.debug("File uploaded successfully.")
                    logging.debug(f"{response}")
                else:
                    logging.error("File upload failed.")

                # Remove the file after sending it
                os.remove(generated_file_path)
                logging.debug(f"Removed file after sending: {generated_file_path}")
                return response
            else:
                logging.error(f"Generated file not found: {generated_file_path}")
                return jsonify({'message': 'Image generation successful, but file not found', 'save_dir': save_dir}), 200
        else:
            logging.error("Image generation failed")
            return jsonify({'message': 'Image generation failed', 'error': result.stderr}), 500

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500


import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
