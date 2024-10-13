import argparse
import os
import logging
import glob
from s3_utils import upload_file_to_s3
from dotenv import load_dotenv

if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv("/home/ubuntu/text2vid-viewer/.env")

    # Set log filename to /app/logs/inference.log if exists else /home/ubuntu/logs/inference.log
    log_filename = '/app/logs/inference.log' if os.path.exists('/app/logs') else '/home/ubuntu/logs/inference.log'

   # Configure logging to file
    logging.basicConfig(filename=log_filename,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__) 
     
    # Parse `model` argument
    parser = argparse.ArgumentParser(description="Send generated videos to S3")
    parser.add_argument("--model", type=str, required=True, help="Name of the model configuration to use")
    args = parser.parse_args()
    model = args.model

    # Export to S3
    generated_files = glob.glob(os.path.join("/home/ubuntu/data", '*.mp4'))
    for generated_file_path in generated_files:
        prompt = os.path.basename(generated_file_path).split('.mp4')[0]
        prompt = prompt.strip().strip('\"').strip('\'').strip('\n') # clean up leading and training space or quotation marks, new line characters
        bucket_name = "text2videoviewer"
        object_name = f"{model}/{prompt}.mp4"
        response = upload_file_to_s3(generated_file_path, bucket_name, object_name)

        if response is not None:
            logger.debug(f"File {generated_file_path} uploaded successfully as {response}.")
            os.remove(generated_file_path)
            logger.debug(f"Removed file after sending: {generated_file_path}")
        else:
            logger.error(f"File upload failed for {generated_file_path}.")