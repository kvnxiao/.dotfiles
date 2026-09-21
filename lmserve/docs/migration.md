# Model serving migrations

## Refresh deployed configuration links

After moving the repository configuration to `lmserve/`, preview and apply the
new symlink sources from the dotfiles repository:

```shell
patina apply
patina apply --yes
```

The deployed model configuration stays under `~/.config/lmserve/`, and Podman
settings stay under `~/.config/containers/`. Refresh these links before using
the deployed Compose path. If replacing Quadlet services, follow
[the Quadlet cutover](#cut-over-from-quadlet) to stop them before deploying.

## Upgrade lmserve repository caches and entry names

Existing standalone repository preparations require an explicit `update-models`
before the updated vLLM services can start. Renamed entries also need
`update-images` and `update-models`: lmserve records image and model preparations
by project and entry name. Install the CLI from a checkout containing
configuration discovery (commit `cd00c3c` or newer):

```shell
cargo install --path ~/github/lmserve/lmserve --locked --force
```

With the updated Compose file and tuning YAMLs deployed, use a directory without
a local `compose.yaml`. Stop the affected active
entry using its old name and inspect its status. Recorded deployments remain
addressable for shutdown after their names are removed from Compose:

```shell
lmserve validate
lmserve stop gemma-4-31b
lmserve status gemma-4-31b
```

Stop is asynchronous. Repeat `status` until the stop operation reports `stopped`;
do not prepare models while it is still stopping. Then prepare and start under the new name:

```shell
lmserve update-images gemma4-31b
lmserve update-models gemma4-31b
lmserve start gemma4-31b
lmserve status gemma4-31b
lmserve health gemma4-31b
```

Repeat `status` and `health` until startup reports `ready` and health succeeds.
Use the corresponding old name for shutdown and new name for preparation and
startup:

| Old entry                 | New entry                |
| ------------------------- | ------------------------ |
| `gemma-4-31b`             | `gemma4-31b`             |
| `gemma-4-31b-abliterated` | `gemma4-31b-abliterated` |
| `qwen-3.8-27b-ninfer`     | `qwen3.8-27b-ninfer`     |

The `qwen-3.8-27b` vLLM entry is removed. If it is active, stop it with
`lmserve stop qwen-3.8-27b` and wait for `lmserve status qwen-3.8-27b` to report
`stopped` before preparing another entry. The NInfer Qwen entries remain available.

An already stopped entry needs preparation under its new name before its next
start; only one model can run at a time. NInfer retains its single-file artifact
mount and follows the same rename procedure.

Let `update-models` publish the compatible cache and clean eligible superseded
content. Do not edit lmserve state or convert or delete cache directories by hand. See the
[lmserve README](../README.md#prepare-and-start-a-model) for cache and revision
configuration.

## Cut over from Quadlet

The repository migration replaces Quadlet units and the Fish helper with the
Rust CLI and one Compose file. Deploying these files does not prepare models or
transfer running containers into `lmserve` ownership.

### Check prerequisites

Use the installed Rust binary to bypass a Fish function still loaded in the
current shell:

```shell
command lmserve --help
podman-compose --version
cd ~/.dotfiles/lmserve
command lmserve validate
```

Use native `podman-compose` 1.6.0; `lmserve` accepts versions 1.5.0 and newer.
Confirm the existing WebUI data volume before stopping the old services:

```shell
podman volume inspect open-webui-data
systemctl --user list-units --all 'vllm-*.service' 'ninfer-*.service' 'open-webui.service'
podman ps --format '{{.Names}} {{.Status}}'
```

### Stop old services and deploy

Stop the loaded model services and WebUI before starting any Compose entry:

```shell
systemctl --user stop 'vllm-*.service' 'ninfer-*.service' open-webui.service ai-net-network.service
patina apply
patina apply --yes
systemctl --user daemon-reload
```

Inspect the Patina preview for the new Compose link and removal of managed
Quadlet, NInfer overlay, and Fish helper links. Patina does not own manually
created Quadlet drop-ins, including the old NInfer `artifact.conf` mount.
Archive any remaining model `.container.d` directories under
`~/.config/containers/systemd/` if they are no longer needed. Keep
`open-webui-data`, model caches, and CDI configuration.

In an existing Fish session, clear the loaded helper before using the binary:

```fish
functions --erase lmserve _lmserve-build _lmserve-download _lmserve-cdi
```

New shells resolve the Rust binary directly. Inspect `podman ps` again and stop
any remaining old model or WebUI containers before starting `lmserve`; the CLI
does not adopt them.

### Prepare and verify

Choose an entry from the [model guides](models/README.md). For example:

```shell
lmserve cdi
lmserve validate
lmserve update-images gemma4-31b
lmserve update-models gemma4-31b
lmserve plan start gemma4-31b
lmserve start gemma4-31b
lmserve status gemma4-31b
lmserve health gemma4-31b
```

Wait for readiness, then check `http://localhost:8080` for existing chat history
and the selected model. `update-models` prepares a separate managed artifact;
the old Hugging Face cache alone does not satisfy startup.

After a failed start, inspect `lmserve status ENTRY` and `lmserve logs ENTRY`,
then use `lmserve stop ENTRY`. Wait until `lmserve status ENTRY` reports the stop
operation as `stopped` before preparing artifacts or retrying startup. See the
[lmserve README](../README.md) for switching engines and updating models.
