import torch
from safetensors.torch import save_file
import json
import os

def convert(input_dpath, output_dpath):
    # Load the JSON file that maps the weights to the respective binary files
    with open(f'{input_dpath}/pytorch_model.bin.index.json', 'r') as f:
        data = json.load(f)

    weight_map = data['weight_map']

    # Initialize a dictionary to hold the model's tensors
    model_weights = {}

    # Load the weights from the binary files
    for param_name, bin_file in weight_map.items():
        bin_file = f"{input_dpath}/{bin_file}"
        # Ensure the bin file exists
        if not os.path.exists(bin_file):
            raise FileNotFoundError(f"File {bin_file} not found")
        # Load the specific tensor from the bin file
        tensor = torch.load(bin_file, map_location='cpu')[param_name]
        model_weights[param_name] = tensor

    # Save all the tensors into a single safetensor file
    save_file(model_weights, f'{output_dpath}/model.safetensors')

    print("Model successfully converted to safetensors!")

if __name__ == '__main__':
    
    input_dpath = "/home/ubuntu/models--lambdalabs--OpenSora-STDiT-v3-Lambda/snapshots/5cde91be1df6da56b6b70ed5e943e0bc2cb38b9b/model"
    output_dpath = "/home/ubuntu"
    convert(input_dpath, output_dpath)