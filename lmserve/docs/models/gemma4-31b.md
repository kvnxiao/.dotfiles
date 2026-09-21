# Gemma 4 31B

The `gemma4-31b` entry uses
`LilaRest/gemma-4-31B-it-NVFP4-turbo` with ModelOpt quantization. Its NVFP4
configuration targets a Blackwell GPU with a compatible CUDA/vLLM image.

Using the deployed configuration, prepare and start the entry:

```shell
lmserve update-images gemma4-31b
lmserve update-models gemma4-31b
lmserve start gemma4-31b
lmserve status gemma4-31b
```

The service reads `vllm/gemma4-31b.yaml`, uses a 16K context and FP8 KV cache,
and publishes port `8000`. Its API model name is `gemma4-31b`. vLLM resolves
the upstream repository ID from the prepared local cache. Use
`lmserve switch gemma4-31b` if another entry is active.
