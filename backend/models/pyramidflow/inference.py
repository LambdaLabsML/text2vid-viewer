import torch
from PIL import Image
from pyramid_dit import PyramidDiTForVideoGeneration
from diffusers.utils import load_image, export_to_video


def dl_model():
    from huggingface_hub import snapshot_download
    model_path = '/home/ubuntu/text2video-viewer/backend/models/pyramidflow/'   # The local directory to save downloaded checkpoint
    snapshot_download("rain1011/pyramid-flow-sd3", local_dir=model_path, local_dir_use_symlinks=False, repo_type='model')


def run_inference():
    torch.cuda.set_device(0)
    model_dtype, torch_dtype = 'bf16', torch.bfloat16   # Use bf16 (not support fp16 yet)

    MODEL_PATH = "/home/ubuntu/text2video-viewer/backend/models/pyramidflow/"
    model = PyramidDiTForVideoGeneration(
        MODEL_PATH,
        model_dtype,
        model_variant='diffusion_transformer_768p',     # 'diffusion_transformer_384p'
    )

    model.vae.to("cuda")
    model.dit.to("cuda")
    model.text_encoder.to("cuda")
    model.vae.enable_tiling()


    prompt = "A movie trailer featuring the adventures of the 30 year old space man wearing a red wool knitted motorcycle helmet, blue sky, salt desert, cinematic style, shot on 35mm film, vivid colors"

    with torch.no_grad(), torch.cuda.amp.autocast(enabled=True, dtype=torch_dtype):
        frames = model.generate(
            prompt=prompt,
            num_inference_steps=[20, 20, 20],
            video_num_inference_steps=[10, 10, 10],
            height=768,     
            width=1280,
            temp=16,                    # temp=16: 5s, temp=31: 10s
            guidance_scale=9.0,         # The guidance for the first frame, set it to 7 for 384p variant
            video_guidance_scale=5.0,   # The guidance for the other video latent
            output_type="pil",
            save_memory=True,           # If you have enough GPU memory, set it to `False` to improve vae decoding speed
        )

    export_to_video(frames, "./text_to_video_sample.mp4", fps=24)

if __name__ == "__main__":

    dl_model()
    run_inference()