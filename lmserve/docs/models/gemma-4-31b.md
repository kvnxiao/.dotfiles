# Gemma 4 31B

The `gemma-4-31b` entry uses
`LilaRest/gemma-4-31B-it-NVFP4-turbo` with ModelOpt quantization. Its NVFP4
configuration targets a Blackwell GPU with a compatible CUDA/vLLM image.

Using the deployed configuration, prepare and start the entry:

```shell
lmserve update-images gemma-4-31b
lmserve update-models gemma-4-31b
lmserve start gemma-4-31b
lmserve status gemma-4-31b
```

The service reads `vllm/gemma-4-31b.yaml`, uses a 16K context and FP8 KV cache,
and publishes port `8000`. Its API model name remains
`LilaRest/gemma-4-31B-it-NVFP4-turbo`. vLLM resolves that repository ID from the
prepared local cache. Use `lmserve switch gemma-4-31b` if another entry is active.
