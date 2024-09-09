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
    config_file = f'/text2vid-viewer/backend/inference/configs/{config}'

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
                response = send_file(generated_file_path, as_attachment=True)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
