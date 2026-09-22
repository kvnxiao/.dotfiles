# Swift Qwen 3.8 27B OrcaRouter

The `qwen3.8-27b-swift-orcarouter` entry serves
[kvnxiao/swift-qwen3.8-27b-orcarouter-dflash2-nvfp4-ninfer](https://huggingface.co/kvnxiao/swift-qwen3.8-27b-orcarouter-dflash2-nvfp4-ninfer).
Compose pins revision `b1ec30022cf61aece82b41d849c4b181f7ddd4c4` and downloads
`swift-qwen3.8-27b-orcarouter-dflash2-nvfp4.ninfer`. The artifact is a conversion of ajgazin's
OrcaRouter-direction Swift checkpoint and includes vision, MTP, DFlash2, and a proposal head.
Attribution, license terms, conversion details, and
[measured results](https://huggingface.co/kvnxiao/swift-qwen3.8-27b-orcarouter-dflash2-nvfp4-ninfer/blob/b1ec30022cf61aece82b41d849c4b181f7ddd4c4/RESULTS.md)
are in the model repository.

## Runtime and memory

The Compose command sets both context and KV capacity to 131,072 tokens, uses FP8 KV cache, and
allows one concurrent request. It enables DFlash2 with seven draft tokens, vision, preserved
thinking, and 4,096 MiB of host KV storage. Host KV storage uses system RAM; it does not replace the
configured GPU KV capacity.

The artifact passed local RTX 5090 validation at 32K context. This 128K profile has not been
GPU-tested. Estimated total GPU use is approximately 28.7 GiB, including desktop use; actual use
varies with inputs, runtime allocations, and other applications. The estimate does not guarantee
that the profile fits. Configure clients to compact conversation history around 100K–110K tokens,
leaving room for generation and request formatting within the 128K context.

The image is `localhost/swift-orcarouter-ninfer:9e163eee4b8a-cuda13.1.2`. The local image was
validated with the artifact at 32K. `ninfer/Dockerfile` builds NInfer commit
`9e163eee4b8acec21ab0ac765107b6a3f287b217` with CUDA 13.1.2 and two compilation workers. The
original `qwen3.8-27b-ninfer` entry retains its separate image and mutable upstream build.

## Prepare and start

With the deployed configuration, prepare the image and model without loading the model onto the GPU:

```shell
lmserve plan update-images qwen3.8-27b-swift-orcarouter
lmserve update-images qwen3.8-27b-swift-orcarouter
lmserve update-models qwen3.8-27b-swift-orcarouter
```

When enough GPU memory is free, start the entry:

```shell
lmserve plan start qwen3.8-27b-swift-orcarouter
lmserve start qwen3.8-27b-swift-orcarouter
lmserve status qwen3.8-27b-swift-orcarouter
lmserve health qwen3.8-27b-swift-orcarouter
```

If another entry is active, use `lmserve switch qwen3.8-27b-swift-orcarouter` instead of `start`.
Repeat `status` and `health` until startup reports ready and health succeeds. Inspect engine logs
with `lmserve logs qwen3.8-27b-swift-orcarouter --follow`.

The API model name is `qwen3.8-27b-swift-orcarouter`. NInfer listens on container port `8080` and
publishes `http://localhost:8001/v1`; Open WebUI uses `http://ninfer:8080/v1` and is available at
`http://localhost:8080`. Readiness checks `http://127.0.0.1:8001/health` with a 900-second timeout.
