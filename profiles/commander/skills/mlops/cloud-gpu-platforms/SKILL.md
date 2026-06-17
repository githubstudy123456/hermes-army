---
name: cloud-gpu-platforms
description: Deploy ML workloads on serverless GPU cloud platforms — auto-scaling APIs, batch jobs, inference endpoints. Covers Modal and general multi-cloud GPU orchestration patterns.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [Cloud GPU, Serverless, Infrastructure, Deployment, GPU, MLops, Modal, RunPod, Lambda Labs, SkyPilot]
---

# Cloud GPU Platforms

Run ML workloads on serverless GPU infrastructure without managing servers. Define compute in code, deploy instantly, scale to zero or to hundreds of GPUs on demand.

## When to Use

Trigger when the user wants to:
- Deploy an ML model as a scaling API endpoint
- Run batch GPU jobs (training, inference, data processing)
- Access on-demand GPU compute without provisioning
- Prototype ML applications quickly
- Run scheduled/cron ML workloads

## Available Platforms

### Modal (Primary)

> **Source skill:** `modal-serverless-gpu`

Serverless GPU cloud with Python-native infrastructure, sub-second cold starts, and auto-scaling. Best for most ML deployment scenarios.

**Use when:** You want the simplest path from Python function to scaled GPU endpoint, with minimal infrastructure boilerplate.

**Key features:**
- Python-first API (`@app.function(gpu="A100")`)
- Auto-scaling to 100+ GPUs
- Sub-second cold starts (Rust-based)
- Container caching for fast iteration
- Web endpoints, scheduled jobs, dynamic batching
- Pay-per-second GPU pricing

### Alternatives

| Platform | Best For | Distinctive Feature |
|----------|----------|---------------------|
| **RunPod** | Longer-running pods with persistent state | Pod-based with persistent storage |
| **Lambda Labs** | Reserved GPU instances | On-demand reserved instances |
| **SkyPilot** | Multi-cloud orchestration | Unified interface across clouds |
| **Kubernetes** | Complex multi-service architectures | Full container orchestration |

---

## Modal — Quick Start

```bash
pip install modal
modal setup  # Browser auth
```

### Hello World with GPU

```python
import modal

app = modal.App("hello-gpu")

@app.function(gpu="T4")
def gpu_info():
    import subprocess
    return subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout

@app.local_entrypoint()
def main():
    print(gpu_info.remote())
```

Run: `modal run hello_gpu.py`

### Inference Endpoint

```python
import modal

app = modal.App("text-generation")
image = modal.Image.debian_slim().pip_install("transformers", "torch", "accelerate")

@app.cls(gpu="A10G", image=image)
class TextGenerator:
    @modal.enter()
    def load_model(self):
        from transformers import pipeline
        self.pipe = pipeline("text-generation", model="gpt2", device=0)

    @modal.method()
    def generate(self, prompt: str) -> str:
        return self.pipe(prompt, max_length=100)[0]["generated_text"]

@app.local_entrypoint()
def main():
    print(TextGenerator().generate.remote("Hello, world"))
```

### Deploy: `modal deploy script.py`

## Modal — Core Concepts

| Component | Purpose |
|-----------|---------|
| `App` | Container for functions and resources |
| `Function` | Serverless function with compute specs |
| `Cls` | Class with lifecycle hooks (`@modal.enter()`) |
| `Image` | Container image definition |
| `Volume` | Persistent storage (model cache, data) |
| `Secret` | Secure credential storage |

### Execution Modes

| Command | Description |
|---------|-------------|
| `modal run script.py` | Execute and exit |
| `modal serve script.py` | Development with live reload |
| `modal deploy script.py` | Persistent cloud deployment |

## Modal — GPU Configuration

### Available GPUs

| GPU | VRAM | Best For |
|-----|------|----------|
| `T4` | 16GB | Budget inference, small models |
| `L4` | 24GB | Inference, Ada Lovelace |
| `A10G` | 24GB | Training/inference, 3.3x faster than T4 |
| `L40S` | 48GB | Recommended inference (best cost/perf) |
| `A100-40GB` | 40GB | Large model training |
| `A100-80GB` | 80GB | Very large models |
| `H100` | 80GB | Fastest, FP8 + Transformer Engine |
| `H200` | 141GB | Auto-upgrade from H100 |
| `B200` | Latest | Blackwell architecture |

### GPU Patterns

```python
# Single GPU
@app.function(gpu="A100")

# Specific memory variant
@app.function(gpu="A100-80GB")

# Multiple GPUs (up to 8)
@app.function(gpu="H100:4")

# Fallback chain
@app.function(gpu=["H100", "A100", "L40S"])

# Any available
@app.function(gpu="any")
```

## Modal — Container Images

```python
# Basic with pip
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.1.0", "transformers==4.36.0", "accelerate"
)

# CUDA base
image = modal.Image.from_registry(
    "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
    add_python="3.11"
).pip_install("torch", "transformers")

# With system packages
image = modal.Image.debian_slim().apt_install("git", "ffmpeg").pip_install("whisper")
```

## Modal — Persistent Storage

```python
volume = modal.Volume.from_name("model-cache", create_if_missing=True)

@app.function(gpu="A10G", volumes={"/models": volume})
def load_model():
    import os
    model_path = "/models/llama-7b"
    if not os.path.exists(model_path):
        model = download_model()
        model.save_pretrained(model_path)
        volume.commit()  # Persist changes
    return load_from_path(model_path)
```

## Modal — Web Endpoints

```python
# FastAPI endpoint
@app.function()
@modal.fastapi_endpoint(method="POST")
def predict(text: str) -> dict:
    return {"result": model.predict(text)}

# Full ASGI app
from fastapi import FastAPI
web_app = FastAPI()

@web_app.post("/predict")
async def predict(text: str):
    return {"result": await model.predict.remote.aio(text)}

@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app
```

| Decorator | Use Case |
|-----------|----------|
| `@modal.fastapi_endpoint()` | Simple function → API |
| `@modal.asgi_app()` | FastAPI/Starlette apps |
| `@modal.wsgi_app()` | Django/Flask apps |

## Modal — Dynamic Batching

```python
@app.function()
@modal.batched(max_batch_size=32, wait_ms=100)
async def batch_predict(inputs: list[str]) -> list[dict]:
    return model.batch_predict(inputs)
```

## Modal — Secrets

```bash
modal secret create huggingface HF_TOKEN=***
```

```python
@app.function(secrets=[modal.Secret.from_name("huggingface")])
def download_model():
    import os
    token = os.environ["HF_TOKEN"]
```

## Modal — Scheduling

```python
@app.function(schedule=modal.Cron("0 0 * * *"))  # Daily midnight
def daily_job():
    pass

@app.function(schedule=modal.Period(hours=1))
def hourly_job():
    pass
```

## Modal — Performance

### Cold Start Mitigation

```python
@app.function(
    container_idle_timeout=300,  # Keep warm 5 min
    allow_concurrent_inputs=10,
)
def inference():
    pass
```

### Model Loading (Use `@modal.enter()`)

```python
@app.cls(gpu="A100")
class Model:
    @modal.enter()  # Run once at container start
    def load(self):
        self.model = load_model()  # Load during warm-up

    @modal.method()
    def predict(self, x):
        return self.model(x)
```

## Modal — Parallel Processing

```python
@app.function()
def process_item(item):
    return expensive_computation(item)

@app.function()
def run_parallel():
    items = list(range(1000))
    results = list(process_item.map(items))  # Fan out to parallel containers
    return results
```

## Modal — Common Configuration

```python
@app.function(
    gpu="A100",
    memory=32768,              # 32GB RAM
    cpu=4,                     # 4 CPU cores
    timeout=3600,              # 1 hour max
    container_idle_timeout=120, # Keep warm 2 min
    retries=3,                 # Retry on failure
    concurrency_limit=10,       # Max concurrent containers
)
def my_function():
    pass
```

## Modal — Troubleshooting

| Issue | Solution |
|-------|----------|
| Cold start latency | Increase `container_idle_timeout`, use `@modal.enter()` |
| GPU OOM | Use larger GPU (`A100-80GB`), enable gradient checkpointing |
| Image build fails | Pin dependency versions, check CUDA compatibility |
| Timeout errors | Increase `timeout`, add checkpointing |

## References

- `references/modal.md` — Full Modal reference content absorbed from `modal-serverless-gpu`
- `references/troubleshooting.md` — Common issues and solutions