resolution = "720p"
aspect_ratio = "9:16"
num_frames = "4s"
fps = 24
frame_interval = 1
save_fps = 24

save_dir = "/data"
seed = 42
batch_size = 1
multi_resolution = "STDiT2"
dtype = "bf16"
condition_frame_length = 5
align = 5

import os

model = dict(
    type="STDiT3-XL/2",
    from_pretrained="eolecvk/OpenSora-STDiT-v3-Lambda",
    qk_norm=True,
    enable_flash_attn=True,
    enable_layernorm_kernel=True,
    force_huggingface=True,
    token=os.getenv('HF_TOKEN')
)
vae = dict(
    type="OpenSoraVAE_V1_2",
    from_pretrained="hpcai-tech/OpenSora-VAE-v1.2",
    micro_frame_size=17,
    micro_batch_size=4,
    force_huggingface=True,
)
text_encoder = dict(
    type="t5",
    from_pretrained="DeepFloyd/t5-v1_1-xxl",
    model_max_length=300,
)
scheduler = dict(
    type="rflow",
    use_timestep_transform=True,
    num_sampling_steps=30,
    cfg_scale=7.0,
)

aes = 6.5
flow = None