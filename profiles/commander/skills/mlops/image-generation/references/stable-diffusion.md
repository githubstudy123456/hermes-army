# Stable Diffusion — Extended Reference

> Absorbed from: `stable-diffusion-image-generation` skill (now archived)

## SDXL Quality Workflow

```python
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
import torch

# Load SDXL with optimizations
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

# Generate with quality settings
image = pipe(
    prompt="A majestic lion in the savanna, golden hour lighting, 8k, detailed fur",
    negative_prompt="blurry, low quality, cartoon, anime, sketch",
    num_inference_steps=30,
    guidance_scale=7.5,
    height=1024,
    width=1024
).images[0]
```

## Fast Prototyping with LCM

```python
from diffusers import AutoPipelineForText2Image, LCMScheduler

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
).to("cuda")

# Load LCM LoRA for fast generation
pipe.load_lora_weights("latent-consistency/lcm-lora-sdxl")
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.fuse_lora()

# Generate in ~1 second
image = pipe(
    "A beautiful landscape",
    num_inference_steps=4,
    guidance_scale=1.0
).images[0]
```

## Model Variants — Precision Loading

```python
# FP16 (recommended for GPU)
pipe = DiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    variant="fp16"
)

# BF16 (better precision, requires Ampere+ GPU)
pipe = DiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16
)
```

## Custom VAE

```python
from diffusers import AutoencoderKL

# Load custom VAE
vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse")

pipe = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    vae=vae,
    torch_dtype=torch.float16
)
```

## Architecture — Three-Pillar Design

```
Pipeline (orchestration)
├── Model (neural networks)
│   ├── UNet / Transformer (noise prediction)
│   ├── VAE (latent encoding/decoding)
│   └── Text Encoder (CLIP/T5)
└── Scheduler (denoising algorithm)
```

### Pipeline Inference Flow

```
Text Prompt → Text Encoder → Text Embeddings
                                    ↓
Random Noise → [Denoising Loop] ← Scheduler
                      ↓
               Predicted Noise
                      ↓
              VAE Decoder → Final Image
```

## Multiple LoRAs with Adapter Weights

```python
# Load multiple LoRAs
pipe.load_lora_weights("lora1", adapter_name="style")
pipe.load_lora_weights("lora2", adapter_name="character")

# Set different weights for each
pipe.set_adapters(["style", "character"], adapter_weights=[0.7, 0.5])

# Generate
image = pipe("A portrait").images[0]
```

## Common Issues — Troubleshooting

### CUDA Out of Memory

```python
# Enable all memory optimizations
pipe.enable_model_cpu_offload()
pipe.enable_attention_slicing()
pipe.enable_vae_slicing()

# Or use lower precision
pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
```

### Black/Noise Images

```python
# Check VAE configuration
# Use safety checker bypass if needed
pipe.safety_checker = None

# Ensure proper dtype consistency
pipe = pipe.to(dtype=torch.float16)
```

### Slow Generation

```python
# Use faster scheduler
from diffusers import DPMSolverMultistepScheduler
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# Reduce steps
image = pipe(prompt, num_inference_steps=20).images[0]
```

## Advanced — Custom Pipelines

```python
from diffusers import DiffusionPipeline, UNet2DConditionModel

# Build custom pipeline with modified UNet
unet = UNet2DConditionModel.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    subfolder="unet",
    torch_dtype=torch.float16
)

pipe = DiffusionPipeline(
    unet=unet,
   vae=pipe.vae,
    text_encoder=pipe.text_encoder,
    tokenizer=pipe.tokenizer,
    scheduler=pipe.scheduler,
    safety_checker=pipe.safety_checker,
    feature_extractor=pipe.feature_extractor,
)
```

## Fine-tuning Reference

For LoRA or DreamBooth fine-tuning, see the `fine-tuning-with-trl` skill. For inference-only LoRA loading, see the LoRA section in the main SKILL.md.

## Resources

- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [Model Hub](https://huggingface.co/models?library=diffusers)
- [SDXL Community Models](https://civitai.com) (various fine-tunes)