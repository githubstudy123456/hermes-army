# Modal — Full Reference

> Absorbed from: `modal-serverless-gpu` skill (now archived)

## Advanced Usage

### Multi-GPU Training

```python
@app.function(gpu="A100:4", cloud="aws")
def distributed_train():
    import torch.distributed as dist
    dist.init_process_group(backend="nccl")
    # Use torch.distributed for multi-GPU training
```

### Scheduled Batch Jobs

```python
@app.function(schedule=modal.Cron("0 2 * * *"))  # 2 AM daily
def nightly_batch_inference():
    dataset = load_dataset()
    results = []
    for batch in dataset.iter_batches(32):
        results.extend(model.predict.batch(batch))
    save_results(results)
```

### Async Web Endpoints

```python
@app.function()
@modal.fastapi_endpoint(method="POST")
async def async_predict(text: str) -> dict:
    # Async allows concurrent model calls
    result = await model.predict.remote.aio(text)
    return {"result": result, "status": "ok"}
```

### Remote Image Building

```python
image = (
    modal.Image.from_dockerfile("Dockerfile")
    .pip_install("torch", "transformers")
    .run_function(download_base_model)  # Pre-populate during build
)
```

### Using Modal Volumes for Checkpointing

```python
volume = modal.Volume.from_name("checkpoints", create_if_missing=True)

@app.function(gpu="A100", volumes={"/checkpoints": volume})
def train_with_checkpoints(epoch: int):
    import os
    ckpt_path = f"/checkpoints/epoch_{epoch}.pt"
    if os.path.exists(ckpt_path):
        model.load_state_dict(load(ckpt_path))
    # training loop
    save(model.state_dict(), ckpt_path)
    volume.commit()
```

## Cost Optimization

### Spot/Preemptible Instances

```python
@app.function(gpu="A100", spot=True)
def cheap_training():
    # Use interruptible instances at ~60% discount
    pass
```

### Scale-to-Zero Configuration

```python
@app.function(
    container_idle_timeout=60,  # Scale to zero after 60s idle
    allow_concurrent_inputs=1,
)
def light_inference():
    pass
```

### Memory Optimization

```python
@app.function(gpu="T4", memory=16384)  # Cap memory to reduce cost
def optimized_inference():
    import gc
    gc.collect()
    # Inference with aggressive cleanup
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Image build timeout` | Slow package installation | Pin versions, use `debian_slim` base |
| `GPU not available` | Wrong region/spot exhaustion | Try fallback GPU chain: `gpu=["A100", "L40S"]` |
| `Volume mount failed` | Volume not created | Create with `create_if_missing=True` |
| `Cold start timeout` | Model too large | Use `@modal.enter()` + `container_idle_timeout` |
| `Secret not found` | Wrong secret name | Verify with `modal secret list` |

## Debugging Tips

```python
# Local execution (no GPU needed, faster iteration)
if __name__ == "__main__":
    result = my_function.local()

# Inspect deployed app
# modal app list
# modal app logs my-app

# Interactive shell in container
# modal debug <function_name>
```

## Environment Variables

```python
import os

@app.function(secrets=[modal.Secret.from_name("my-secrets")])
def use_env():
    api_key = os.environ["API_KEY"]  # From secret
    debug = os.environ.get("DEBUG", "false")  # Optional var
```

## Modal Python API Reference

| Class/Decorator | Description |
|-----------------|-------------|
| `modal.App` | Top-level application container |
| `@app.function()` | Serverless function |
| `@app.cls()` | Class with lifecycle hooks |
| `@modal.enter()` | Run once at container start (warm-up) |
| `@modal.exit()` | Run at container shutdown |
| `@modal.method()` | HTTP-accessible method on a class |
| `modal.Image` | Container image builder |
| `modal.Volume` | Persistent storage |
| `modal.Secret` | Credential storage |
| `modal.Cron` | Cron schedule |
| `modal.Period` | Periodic schedule |
| `modal.batched()` | Dynamic request batching |

## Resources

- [Modal Docs](https://modal.com/docs)
- [Modal Examples](https://github.com/modal-labs/modal-examples)
- [Pricing](https://modal.com/pricing)