# Gemma 4 31B abliterated

The `gemma-4-31b-abliterated` entry uses
`NeuralNet-Hub/gemma-4-31B-it-abliterated-uncensored-NVFP4`.

Using the deployed configuration, prepare and start the entry:

```shell
lmserve update-images gemma-4-31b-abliterated
lmserve update-models gemma-4-31b-abliterated
lmserve start gemma-4-31b-abliterated
lmserve status gemma-4-31b-abliterated
```

The service reads `vllm/gemma-4-31b-abliterated.yaml`, uses a 32K context and
FP8 KV cache, and publishes port `8000`. Its API model name is
`gemma-4-31b-abliterated`. Use `lmserve switch gemma-4-31b-abliterated` if
another entry is active.
