# Container stack

Rootless Podman runs one model server and the Open WebUI frontend on the
`ai-net` network. Quadlet files under
`~/.config/containers/systemd/` generate user services managed with
`systemctl --user`.

## Services

| Unit             | Engine     | Network alias | Published port |
| ---------------- | ---------- | ------------- | -------------- |
| `ninfer-qwen3.8` | NInfer     | `ninfer:8080` | `8001`         |
| `vllm-qwen3.8`   | vLLM       | `vllm:8000`   | `8000`         |
| `vllm-gemma4`    | vLLM       | `vllm:8000`   | `8000`         |
| `open-webui`     | Open WebUI | None          | `8080`         |

Open WebUI reads these backend URLs:

```text
http://vllm:8000/v1;http://ninfer:8080/v1
```

It queries `/v1/models` on each page load and lists the models returned by the
backend that answers. NInfer exposes the model as `qwen3.8-27b`, from the
`--model-id` argument in its unit.

## Service lifecycle

None of the Quadlet units has an `[Install]` section, so no unit is enabled for
automatic startup. Each model service declares
`Wants=open-webui.service`, which starts Open WebUI when a model service starts.
The dependency is one-way: stopping a model does not stop Open WebUI, and
`open-webui.service` has no reverse dependency on a model.

Open WebUI does not need ordering against either model because it re-queries
`/v1/models` when a page loads. Start or stop it independently:

```shell
systemctl --user start open-webui
systemctl --user stop open-webui
```

Each model service declares `Conflicts=` against the other model services. When
one model starts, systemd stops any conflicting model. `Conflicts=` does not
order those jobs, so the outgoing container can still hold VRAM when the
incoming container reaches CUDA initialization.

The model services use a one-directional ordering chain:

```text
ninfer-qwen3.8.service → vllm-qwen3.8.service → vllm-gemma4.service
```

The `After=` edges order the incumbent's stop before the incoming model's
start. One edge per pair is sufficient because systemd applies the ordering to
the stop jobs in the required direction. Adding the matching reverse
`After=` edge creates a cycle through those stop jobs, which systemd reports as
unfixable.

## Initial setup

Apply the Linux container files before using `lmserve`:

```shell
patina apply --yes
```

A user systemd manager normally runs only during a login session. Enable
lingering to start the user manager at boot and keep it running after logout:

```shell
loginctl enable-linger $USER
```

Lingering does not enable any container unit. Because the units have no
`[Install]` section, it does not start the model or frontend automatically;
start the desired model service explicitly.

The NInfer unit uses `localhost/ninfer:local`. Build that image with:

```shell
lmserve build ninfer
```

The command clones `~/src/ninfer` when the source checkout is absent, builds the
upstream image as `ninfer:base`, and builds `ninfer:local` from
`~/.config/lmserve/ninfer/Containerfile`. The local `Containerfile` adds
`curl`, which the unit uses for its health check.

## Model artifacts

The vLLM services mount their YAML files from
`~/.config/lmserve/vllm/`. At startup, vLLM reads the Hugging Face model ID
from the mounted file. The services run with
`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`, so the model must already be in
the mounted Hugging Face cache.

NInfer loads one `.ninfer` artifact. Download the supported artifact with:

```shell
lmserve download qwen3.8-nvfp4
```

The command downloads
`neroued/Qwen3.8-27B-nvfp4-NInfer/qwen3_8_27b_nvfp4.ninfer` into the Hugging
Face cache, resolves the snapshot path to its blob, and writes a Quadlet
drop-in under:

```text
~/.config/containers/systemd/ninfer-qwen3.8.container.d/artifact.conf
```

The drop-in binds the resolved blob to the path used by the NInfer unit:

```ini
[Container]
Volume=/home/…/blobs/<sha256>:/models/artifact.ninfer:ro
```

Hugging Face stores a snapshot entry as a relative symlink into `blobs/`. That
symlink does not resolve across the bind mount, so the drop-in binds the
resolved blob directly. Run `lmserve download qwen3.8-nvfp4` again after the
upstream repository publishes a new revision.

## Operating the services

Start the NInfer service and inspect its state with:

```shell
systemctl --user start ninfer-qwen3.8
systemctl --user status ninfer-qwen3.8
podman healthcheck run ninfer-qwen3.8
journalctl --user -u ninfer-qwen3.8 -f
```

After editing a Quadlet unit, reload the user manager and restart the service:

```shell
systemctl --user daemon-reload
systemctl --user restart ninfer-qwen3.8
```

## CDI after a Windows NVIDIA driver update

Rootless Podman injects the GPU through the CDI specification at
`~/.config/cdi/nvidia.yaml`. The rendered `containers.conf` names that
directory through `cdi_spec_dirs`; the path is inserted during rendering
because Podman does not expand `~` or `$HOME` in that setting.

The CDI specification references a versioned WSL driver directory under
`/usr/lib/wsl/drivers/`. A Windows NVIDIA driver update replaces that
directory. Host `nvidia-smi` can continue to work while every container using
`--device nvidia.com/gpu=all` fails with:

```text
Error: crun: cannot stat `/usr/lib/wsl/drivers/nv_dispi.inf_amd64_<hash>/NvFBC.dll`:
No such file or directory
```

Regenerate the specification against the installed driver:

```shell
lmserve cdi
```

## VRAM budget

The RTX 5090 has 32,607 MiB. The Windows desktop uses roughly 5 GB under WSL2,
and NInfer's NVFP4 weights occupy about 22 GiB. Under 5 GB remains for the KV
pool and activations.

NInfer requests automatic KV capacity with:

```text
--kv-capacity auto
```

If startup allocation fails, replace it with an explicit token count and lower
`--max-context`.

## WSL2 CUDA allocator

The vLLM units leave `PYTORCH_CUDA_ALLOC_CONF` unset. Setting it to
`expandable_segments:True` makes the Marlin weight repack fail in
`aten::empty` on this setup. The Windows GPU driver rejects the WSL residency
request with error `-12` even while `nvidia-smi` reports free VRAM.

After a failed start, inspect the WSL kernel log:

```shell
sudo dmesg --ctime |
    rg -i 'dxgkio_make_resident|dxgvmb|nvrm|xid|out of memory|oom' |
    tail -n 80
```

This log entry points to the allocator override:

```text
dxgkio_make_resident: Ioctl failed: -12
```

Clearing the Hugging Face weights or the vLLM compilation cache does not
address this failure.
