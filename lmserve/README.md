# Local model serving

`lmserve` runs one model server and its Open WebUI companion through rootless Podman.
[compose.yaml](compose.yaml) defines all vLLM and NInfer entries. Shared vLLM container settings use
YAML anchors; `vllm/` contains the engine tuning files, and `ninfer/` contains the Swift entry's
pinned runtime build. [Model guides](docs/models/README.md) describe each entry.

## Requirements

Install the Rust `lmserve` binary, Podman 4.6 or newer, `podman-compose` 1.5.0 or newer, the Hugging
Face `hf` CLI, and NVIDIA Container Toolkit. The native `podman-compose` 1.6.0 is supported.
Authenticate with `hf auth login` when a model repository requires access.

Rootless Podman reads the NVIDIA CDI specification from `~/.config/cdi/nvidia.yaml`. Generate it
before serving, and regenerate it after an NVIDIA driver update:

```shell
lmserve cdi
```

The vLLM services set `VLLM_WSL2_ENABLE_PIN_MEMORY=1`.

## Deploy configuration

Preview and apply the dotfiles:

```shell
patina apply
patina apply --yes
```

Patina links `compose.yaml` to `~/.config/lmserve/compose.yaml`, the tuning files to
`~/.config/lmserve/vllm/`, and the NInfer build files to `~/.config/lmserve/ninfer/`. With a CLI
that includes configuration discovery (commit `cd00c3c` or newer), run commands from any directory
without a local `compose.yaml`:

```shell
lmserve validate
lmserve list
```

Configuration selection uses this order:

1. An explicit `--file PATH` for an alternate configuration.
2. `./compose.yaml`, when present.
3. `$XDG_CONFIG_HOME/lmserve/compose.yaml`, or `~/.config/lmserve/compose.yaml` when
   `XDG_CONFIG_HOME` is unset or empty.

A selected file that is missing or invalid reports an error without falling back. A nonempty
`XDG_CONFIG_HOME` must be absolute. This repository deploys to `~/.config/lmserve/`; if using
another XDG configuration directory, install the Compose symlink under that directory's `lmserve/`
subdirectory.

`lmserve` canonicalizes the selected file before resolving relative mounts and `.env`. The deployed
symlink therefore resolves `./vllm/` and `./ninfer/` from this repository's `lmserve/` directory.
Keep any project `.env` beside the actual Compose file, not beside its deployed symlink. No `.env`
is currently required.

Before deployment, run `lmserve validate` from this repository's `lmserve/` directory to select the
local Compose file.

## Prepare and start a model

Prepare only the selected entry, including its WebUI image:

```shell
lmserve plan update-images gemma4-31b
lmserve update-images gemma4-31b
lmserve update-models gemma4-31b
lmserve plan start gemma4-31b
lmserve start gemma4-31b
lmserve status gemma4-31b
lmserve health gemma4-31b
```

`start` returns after accepting the operation. `status` reports startup progress; `health` succeeds
when the model endpoint is ready. Readiness allows 900 seconds. Use `lmserve logs ENTRY --follow`
for the engine logs and `lmserve logs ENTRY --service open-webui --follow` for WebUI logs.

For the original NInfer entry, `update-images qwen3.8-27b-ninfer` builds the upstream `master`
Dockerfile directly as `localhost/ninfer:local`. The
[Swift entry](docs/models/qwen3.8-27b-swift-orcarouter.md) uses `ninfer/Dockerfile` to build
`localhost/swift-orcarouter-ninfer:9e163eee4b8a-cuda13.1.2` from a pinned NInfer commit and CUDA
13.1.2, with two compilation workers. `lmserve` checks each entry's `/health` endpoint from the
host.

Model repositories are declared in Compose. The original NInfer entry declares its artifact filename
in `huggingface.file`; Swift declares its `.ninfer` filename in the snapshot path of its NInfer
command. With no `huggingface.revision`, each explicit `update-models` selects the current remote
`main` commit. Swift pins both its model revision and NInfer source commit; the original NInfer
entry follows the mutable source branch. Image tags remain mutable, and preparation records the
resolved image and artifact identities. Lifecycle commands do not pull images, build sources, or
download models.

`update-models` publishes artifacts under `${XDG_CACHE_HOME:-~/.cache}/lmserve/models`, separate
from the default Hugging Face cache. Allow space for staged downloads and published artifacts. The
original NInfer entry mounts only its prepared `.ninfer` artifact. For Swift, `lmserve` downloads
the full repository snapshot and mounts the prepared Hugging Face cache read-only at
`/lmserve/huggingface/hub`, and NInfer loads the `.ninfer` file from the pinned snapshot path.

Each vLLM tuning YAML uses the repository ID declared in `x-lmserve.huggingface.repo`. `lmserve`
mounts its prepared Hugging Face cache read-only at `/lmserve/huggingface/hub` and supplies
`HF_HUB_CACHE=/lmserve/huggingface/hub`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`. The
cache's local `refs/main` selects the exact prepared commit, including when `huggingface.revision`
selects another source branch, tag, or commit. Startup uses this local content without downloading
models.

Keep source revision selection in `x-lmserve.huggingface.revision`; leave vLLM's `revision`,
`tokenizer-revision`, and `code-revision` unset. Leave `download-dir` unset so download locks remain
outside the read-only cache. Do not add model-path mounts or Hugging Face model-cache and offline
variables to vLLM services or their environment files. Keep writable module and compiler caches
outside the managed model cache; the vLLM services mount `~/.cache/vllm` for compilation caches.

`lmserve` prepares only the declared model repository. These tuning files enable `trust-remote-code`
but do not explicitly select separate tokenizer or code repositories. Flag any such dependency
before serving; this interface does not prepare it.

## Switch, restart, and stop

Prepare a different entry before switching to it:

```shell
lmserve update-images qwen3.8-27b-ninfer
lmserve update-models qwen3.8-27b-ninfer
lmserve switch qwen3.8-27b-ninfer
lmserve status qwen3.8-27b-ninfer
lmserve health qwen3.8-27b-ninfer
lmserve stop qwen3.8-27b-ninfer
```

`switch` stops the active model before starting its replacement. An unchanged WebUI companion can
remain running. After editing a vLLM tuning file or model service, use `lmserve restart ENTRY`. When
changing WebUI configuration or its image, use `lmserve stop ENTRY`, wait until
`lmserve status ENTRY` reports the stop operation as `stopped`, then run `lmserve start ENTRY`. Stop
is asynchronous; wait for it to finish before preparing model updates as well.

Use `lmserve` for lifecycle commands; starting the full Compose project directly would select
conflicting model services. There is no automatic model restart after failure, reboot, or WSL
shutdown. Start the chosen entry explicitly. `lmserve` stores ownership and operation records under
`${XDG_STATE_HOME:-~/.local/state}/lmserve`; preserve that state while its containers exist.

## Endpoints and data

| Service    | Host URL                   | WebUI connection              |
| ---------- | -------------------------- | ----------------------------- |
| vLLM       | `http://localhost:8000/v1` | `http://vllm:8000/v1`         |
| NInfer     | `http://localhost:8001/v1` | `http://ninfer:8080/v1`       |
| Open WebUI | `http://localhost:8080`    | Both engine connections above |

Compose publishes the host ports on all interfaces. The WebUI service sets `WEBUI_AUTH=false` and
uses `sk-local` for both connection keys. Only the selected engine endpoint is active.

Compose names the default network `ai-net` and the WebUI volume `open-webui-data`, without the
`lmserve` project prefix. The volume contains WebUI settings and chat history and remains after an
entry stops. Persisted WebUI connection settings may override environment values; inspect its
connections if a model is missing from the UI.

Podman, `lmserve`, and vLLM store data in these host locations:

| Data                                             | Host location                                                     |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| WebUI named volume                               | `~/.local/share/containers/storage/volumes/open-webui-data/_data` |
| Podman images and container storage              | `~/.local/share/containers/storage`                               |
| Prepared model artifacts and Hugging Face caches | `${XDG_CACHE_HOME:-~/.cache}/lmserve/models`                      |
| vLLM compilation caches                          | `~/.cache/vllm`                                                   |

Podman storage paths can vary by configuration; query the volume's actual mountpoint with:

```shell
podman volume inspect open-webui-data --format '{{.Mountpoint}}'
```
