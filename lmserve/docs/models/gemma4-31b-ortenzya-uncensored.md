# Gemma 4 31B Ortenzya uncensored

The `gemma4-31b-ortenzya-uncensored` entry uses
`llmfan46/gemma-4-Ortenzya-The-Creative-Wordsmith-31B-it-uncensored-heretic-NVFP4`.

Using the deployed configuration, prepare and start the entry:

```shell
lmserve update-images gemma4-31b-ortenzya-uncensored
lmserve update-models gemma4-31b-ortenzya-uncensored
lmserve start gemma4-31b-ortenzya-uncensored
lmserve status gemma4-31b-ortenzya-uncensored
```

The service reads `vllm/gemma4-31b-ortenzya-uncensored.yaml`, uses a 32K context and FP8 KV cache,
and publishes port `8000`. Its API model name is `gemma4-31b-ortenzya-uncensored`. If another entry
is active, use `lmserve switch gemma4-31b-ortenzya-uncensored`.
