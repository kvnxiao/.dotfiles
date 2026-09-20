# Qwen 3.8 27B

Qwen has separate vLLM and NInfer entries in the shared Compose file. Run these
commands with the deployed configuration.

## vLLM

The `qwen-3.8-27b` entry uses `cyankiwi/Qwen3.8-27B-AWQ-INT4`:

```shell
lmserve update-images qwen-3.8-27b
lmserve update-models qwen-3.8-27b
lmserve start qwen-3.8-27b
lmserve status qwen-3.8-27b
```

The service reads `vllm/qwen-3.8-27b.yaml`, uses a 128K context and FP8 KV cache,
and publishes port `8000`.

## NInfer

The `qwen-3.8-27b-ninfer` entry uses `qwen3_8_27b_nvfp4.ninfer` from
`neroued/Qwen3.8-27B-nvfp4-NInfer`. Its command retains a 128K context, FP8 KV
cache, MTP speculation with three draft tokens, and 4096 MiB of host KV storage.

Build the image and prepare the artifact before switching from vLLM:

```shell
lmserve update-images qwen-3.8-27b-ninfer
lmserve update-models qwen-3.8-27b-ninfer
lmserve switch qwen-3.8-27b-ninfer
lmserve status qwen-3.8-27b-ninfer
```

If no entry is active, use `lmserve start qwen-3.8-27b-ninfer`. NInfer listens on
container port `8080` and publishes host port `8001`. Both engines expose
`qwen-3.8-27b` as their API model name.
