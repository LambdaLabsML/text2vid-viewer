import os
from huggingface_hub import snapshot_download

def dl_model():
    
    model_path = '/home/ubuntu/text2vid-viewer/backend/models/mochi/weights'   # The local directory to save downloaded checkpoint
    if not os.path.exists(model_path):
        os.makedirs(model_path)
        snapshot_download("genmo/mochi-1-preview", local_dir=model_path, repo_type='model')
    else:
        print(f"Model already exists in the directory: {model_path}")
    


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv("/home/ubuntu/text2vid-viewer/.env")
    dl_model()