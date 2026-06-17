---
name: image-generation
description: Generate images from text (text-to-image), transform existing images (image-to-image), inpaint/mask regions, or use spatial conditioning (ControlNet). Covers Stable Diffusion (via Diffusers), Flux, and related models.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [Image Generation, Text-to-Image, Diffusion, Stable Diffusion, Flux, ControlNet, Inpainting, Image-to-Image, LoRA, Computer Vision]
---

# Image Generation

Generate images from text, transform existing images, inpaint masked regions, or apply spatial conditioning. The primary framework is HuggingFace Diffusers supporting Stable Diffusion (1.5, 2.x, XL, 3.0), Flux, and related architectures.

## When to Use

Trigger when the user wants to:
- Generate an image from a text description (text-to-image)
- Transform or stylize an existing image (image-to-image)
- Fill or replace a region of an image (inpainting/outpainting)
- Apply spatial control (edges, pose, depth) via ControlNet
- Load or apply LoRA style adapters
- Build custom diffusion pipelines

## Core Models

### Stable Diffusion (SD)

The most widely-used open image generation family. Versions:
- **SD 1.5** — Most compatible, largest community support
- **SD 2.0/2.1** — Higher resolution, NSFW filter removed
- **SDXL** — Better quality, 1024px default, more VRAM
- **SD 3.0** — MMDiT architecture, improved prompt following
- **Flux** — Formerly Stable Diffusion 3, non-open weights

### Diffusers Pipeline Reference

| Pipeline | Model Type | Use Case |
|----------|------------|----------|
| `StableDiffusionPipeline` | SD 1.x/2.x text-to-image | Default |
| `StableDiffusionXLPipeline` | SDXL text-to-image | Higher quality |
| `StableDiffusion3Pipeline` | SD 3.0 | Best quality |
| `FluxPipeline` | Flux | Artistic |
| `StableDiffusionImg2ImgPipeline` | SD image-to-image | Style transfer |
| `StableDiffusionInpaintPipeline` | SD inpainting | Masked regions |
| `StableDiffusionControlNetPipeline` | SD + ControlNet | Spatial control |

## Stable Diffusion — Quick Start

```bash
pip install diffusers transformers accelerate torch
pip install xformers  # Optional: memory-efficient attention
```

### Basic text-to-image

```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe.to("cuda")

image = pipe(
    "A serene mountain landscape at sunset, highly detailed",
    num_inference_steps=50,
    guidance_scale=7.5
).images[0]
image.save("output.png")
```

### SDXL (higher quality)

```python
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.to("cuda")
pipe.enable_model_cpu_offload()

image = pipe(
    prompt="A futuristic city with flying cars, cinematic lighting",
    height=1024, width=1024,
    num_inference_steps=30
).images[0]
```

## Image-to-Image

Transform existing images with text guidance:

```python
from diffusers import AutoPipelineForImage2Image
from PIL import Image

pipe = AutoPipelineForImage2Image.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

init_image = Image.open("input.jpg").resize((512, 512))
image = pipe(
    prompt="A watercolor painting of the scene",
    image=init_image,
    strength=0.75,  # 0-1, how much to transform
    num_inference_steps=50
).images[0]
```

## Inpainting

Fill masked regions:

```python
from diffusers import AutoPipelineForInpainting
from PIL import Image

pipe = AutoPipelineForInpainting.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
).to("cuda")

image = Image.open("photo.jpg")
mask = Image.open("mask.png")  # White = inpaint region

result = pipe(
    prompt="A red car parked on the street",
    image=image, mask_image=mask,
    num_inference_steps=50
).images[0]
```

## ControlNet — Spatial Conditioning

Add precise spatial control via edge maps, pose skeletons, depth maps, etc.:

```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_canny",
    torch_dtype=torch.float16
)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to("cuda")

control_image = get_canny_image(input_image)  # Edge-detected input
image = pipe(
    prompt="A beautiful house in the style of Van Gogh",
    image=control_image,
    num_inference_steps=30
).images[0]
```

### Available ControlNet Types

| ControlNet | Input | Use Case |
|------------|-------|----------|
| `canny` | Edge maps | Preserve structure |
| `openpose` | Pose skeletons | Human poses |
| `depth` | Depth maps | 3D-aware generation |
| `normal` | Normal maps | Surface details |
| `scribble` | Sketches | Sketch-to-image |

## LoRA Adapters — Style Customization

Load fine-tuned style or character adapters:

```python
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

# Load LoRA
pipe.load_lora_weights("path/to/lora", weight_name="style.safetensors")
image = pipe("A portrait in the trained style").images[0]

# Adjust strength and fuse
pipe.set_adapters(["style"], adapter_weights=[0.8])
pipe.fuse_lora(lora_scale=0.8)

# Unload when done
pipe.unload_lora_weights()
```

### Multiple LoRAs

```python
pipe.load_lora_weights("lora1", adapter_name="style")
pipe.load_lora_weights("lora2", adapter_name="character")
pipe.set_adapters(["style", "character"], adapter_weights=[0.7, 0.5])
```

## Schedulers — Controlling Denoising

```python
from diffusers import DPMSolverMultistepScheduler, LCMScheduler

# Faster scheduler (15-25 steps)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# Very fast (4-8 steps) — requires LCM LoRA
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
```

| Scheduler | Steps | Quality | Speed |
|-----------|-------|---------|-------|
| `EulerDiscreteScheduler` | 20-50 | Good | Medium |
| `DPMSolverMultistepScheduler` | 15-25 | Excellent | Fast |
| `LCMScheduler` | 4-8 | Good | Very fast |
| `DDIMScheduler` | 50-100 | Good | Slow |

## Memory Optimization

```python
# Model CPU offload — auto-moves models to CPU when idle
pipe.enable_model_cpu_offload()

# Sequential offload — more aggressive
pipe.enable_sequential_cpu_offload()

# Attention slicing — reduces peak VRAM
pipe.enable_attention_slicing()
pipe.enable_attention_slicing("max")

# xFormers — memory-efficient attention (requires xformers package)
pipe.enable_xformers_memory_efficient_attention()

# VAE tiling — for large images
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()
```

## Batch Generation

```python
# Multiple prompts
images = pipe(["A cat", "A dog", "A bird"], num_inference_steps=30).images

# Multiple images per prompt
images = pipe("A sunset", num_images_per_prompt=4, num_inference_steps=30).images
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prompt` | Required | Text description |
| `negative_prompt` | None | What to avoid |
| `num_inference_steps` | 50 | Denoising quality (more = better) |
| `guidance_scale` | 7.5 | Prompt adherence (7-12 typical) |
| `height`, `width` | 512/1024 | Output (multiples of 8) |
| `generator` | None | For reproducibility |

## Stable Diffusion Specifics

> **Source skill:** `stable-diffusion-image-generation`
> Full reference: see `references/stable-diffusion.md`

Contains: SDXL quality workflow, fast prototyping with LCM, model variant loading (FP16/BF16), custom VAE, troubleshooting (OOM, black images, slow generation).

## References

- `references/stable-diffusion.md` — Extended SD usage (SDXL, LCM, variants, troubleshooting)
- `references/advanced-usage.md` — Custom pipelines, fine-tuning, deployment (from original skill)
- `references/troubleshooting.md` — Common issues and solutions (from original skill)

## Resources

- [Diffusers Docs](https://huggingface.co/docs/diffusers)
- [Diffusers GitHub](https://github.com/huggingface/diffusers)
- [Model Hub](https://huggingface.co/models?library=diffusers)