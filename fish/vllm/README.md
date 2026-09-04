# vLLM profiles

The Fish `vllm` function starts one model server and one optional Open WebUI
container on the `ai-net` Podman network. Model IDs and vLLM runtime options live
in native YAML files under `profiles/`.

## Run a profile

Download the model before starting it because model containers run with
Hugging Face offline mode enabled:

```shell
vllm download cyankiwi/Qwen3.8-27B-AWQ-INT4
vllm start cyankiwi/Qwen3.8-27B-AWQ-INT4 --profile qwen3.8
vllm verify cyankiwi/Qwen3.8-27B-AWQ-INT4 --profile qwen3.8
```

The profile override is optional when the model ID contains `qwen3.8`, `gemma-4`,
or `gemma4`. The launcher passes the requested model as vLLM's positional model
argument, which takes precedence over the YAML `model` value. This keeps explicit
model variants possible while each YAML file remains runnable by itself:

```shell
command vllm serve --config fish/vllm/profiles/qwen3.8.yaml
```

The launcher mounts the selected file read-only at `/etc/vllm/config.yaml` and
runs the `docker.io/vllm/vllm-openai:latest` image with
`--config /etc/vllm/config.yaml`.

When an image, profile, or mounted configuration changes, recreate the model
container manually:

```shell
vllm remove cyankiwi/Qwen3.8-27B-AWQ-INT4
vllm start cyankiwi/Qwen3.8-27B-AWQ-INT4 --profile qwen3.8
```

## WSL2 CUDA allocator

On the RTX 5090 WSL2 setup, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
caused the Marlin weight repack to fail in `aten::empty`. The Windows GPU driver
rejected the corresponding WSL residency request with error `-12` even while
`nvidia-smi` reported free VRAM.

Leave `PYTORCH_CUDA_ALLOC_CONF` unset for these containers. Expandable segments
let PyTorch extend CUDA allocator segments to reduce fragmentation, but this mode
is not required for vLLM or FP8 KV cache.

Check the WSL kernel log after a failed start:

```shell
sudo dmesg --ctime |
    rg -i 'dxgkio_make_resident|dxgvmb|nvrm|xid|out of memory|oom' |
    tail -n 80
```

If the log contains `dxgkio_make_resident: Ioctl failed: -12`, remove the
allocator override and recreate the container. Clearing Hugging Face weights or
the vLLM compilation cache is not required for this failure.
