# Qwen 3.8 27B

The `qwen3.8-27b-ninfer` entry uses `qwen3_8_27b_nvfp4.ninfer` from
`neroued/Qwen3.8-27B-nvfp4-NInfer`. Its command retains a 128K context, FP8 KV cache, MTP
speculation with three draft tokens, and 4096 MiB of host KV storage.

Build the image and prepare the artifact before switching from another entry:

```shell
lmserve update-images qwen3.8-27b-ninfer
lmserve update-models qwen3.8-27b-ninfer
lmserve switch qwen3.8-27b-ninfer
lmserve status qwen3.8-27b-ninfer
```

If no entry is active, use `lmserve start qwen3.8-27b-ninfer`. NInfer listens on container port
`8080` and publishes host port `8001`. It exposes `qwen3.8-27b` as its API model name.
