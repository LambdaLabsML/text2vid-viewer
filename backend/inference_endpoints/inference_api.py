from flask import Flask, request, jsonify, send_file
import subprocess
import os
import logging
import glob

app = Flask(__name__)

# Configure logging to file
logging.basicConfig(filename='/data/api_server.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def get_available_gpus():
    """Returns a list of available GPU IDs."""
    try:
        import torch
        available_gpus = list(range(torch.cuda.device_count()))
        return available_gpus
    except Exception as e:
        logging.error(f"Error getting available GPUs: {e}")
        return []

@app.route('/generate', methods=['POST'])
def generate_image():
        
    def get_cmd_list(data, multi_gpu=False):
        num_frames = data.get('num_frames', '4')
        resolution = data.get('resolution', '360p')
        aspect_ratio = data.get('aspect_ratio', '9:16')
        prompt = data.get('prompt', 'a beautiful waterfall')

        if multi_gpu:
            available_gpus = get_available_gpus()
            cuda_visible_devices = ','.join(map(str, available_gpus))
            nproc_per_node = len(available_gpus)

            cmd = [
                'CUDA_VISIBLE_DEVICES=' + cuda_visible_devices,
                'torchrun', '--nproc_per_node', str(nproc_per_node),
                'scripts/inference.py', 'configs/opensora-v1-2/inference/sample.py',
                '--num-frames', num_frames,
                '--resolution', resolution,
                '--aspect-ratio', aspect_ratio,
                '--prompt', prompt,
                '--save-dir', os.environ.get('SAVE_DIR', '/data')
            ]
        else:
            # forcing single GPU until bug resolved https://github.com/orgs/LambdaLabsML/projects/14/views/1?pane=issue&itemId=70850852
            cmd = [
                'python', 'scripts/inference.py',
                'configs/opensora-v1-2/inference/sample.py',
                '--num-frames', num_frames,
                '--resolution', resolution,
                '--aspect-ratio', aspect_ratio,
                '--prompt', prompt,
                '--save-dir', os.environ.get('SAVE_DIR', '/data')
            ]

        logging.debug(f"Running command: {' '.join(cmd)}")
        return cmd

    try:
        data = request.json
        logging.debug(f"Request data: {data}")

        # Remove files with name pattern `sample_*.mp4`
        save_dir = os.environ.get('SAVE_DIR', '/data')
        for file_path in glob.glob(os.path.join(save_dir, 'sample_*.mp4')):
            os.remove(file_path)
            logging.debug(f"Removed file: {file_path}")

        # Run inference cmd
        cmd_list = get_cmd_list(data, multi_gpu=False)
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        logging.debug(f"Command output: {result.stdout}")  
        logging.error(f"Command error output: {result.stderr}")
        
        # if result.returncode == 0:
        #     print("test success")
    #         # Assuming the generated file is saved in the save_dir with a known name
    #         generated_file_path = os.path.join(save_dir, 'sample_0000.mp4')  # Update this with the correct filename
    #         if os.path.exists(generated_file_path):
    #             response = send_file(generated_file_path, as_attachment=True)
    #             # Remove the file after sending it
    #             os.remove(generated_file_path)
    #             logging.debug(f"Removed file after sending: {generated_file_path}")
    #             return response
    #         else:
    #             logging.error(f"Generated file not found: {generated_file_path}")
    #             return jsonify({'message': 'Image generation successful, but file not found', 'save_dir': save_dir}), 200
    #     else:
    #         logging.error("Image generation failed")
    #         return jsonify({'message': 'Image generation failed', 'error': result.stderr}), 500
    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
