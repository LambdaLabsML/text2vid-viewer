def dl_model():
    from huggingface_hub import snapshot_download
    model_path = '/home/ubuntu/text2vid-viewer/backend/models/mochi/'   # The local directory to save downloaded checkpoint
    snapshot_download("genmo/mochi-1-preview", local_dir=model_path, local_dir_use_symlinks=False, repo_type='model')


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv("/home/ubuntu/text2vid-viewer/.env")
    dl_model()