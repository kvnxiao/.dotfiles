# Model profiles

One [Compose file](../../compose.yaml) defines both engines and their shared
Open WebUI companion. Each key under Compose `services` with `x-lmserve`
metadata is an `lmserve` entry name; filenames do not determine it. The
service image and command select the engine.

Use these names in `lmserve start ENTRY` and other lifecycle commands:

| Model                                                 | Entry                          | Engine tuning                           |
| ----------------------------------------------------- | ------------------------------ | --------------------------------------- |
| [Qwen 3.8 27B](qwen3.8-27b.md)                        | `qwen3.8-27b-ninfer`           | Compose command                         |
| [Swift Qwen 3.8 27B OrcaRouter](swift-qwen3.8-27b.md) | `qwen3.8-27b-swift-orcarouter` | Compose command and `ninfer/Dockerfile` |
| [Gemma 4 31B](gemma4-31b.md)                          | `gemma4-31b`                   | `vllm/gemma4-31b.yaml`                  |
| [Gemma 4 31B abliterated](gemma4-31b-abliterated.md)  | `gemma4-31b-abliterated`       | `vllm/gemma4-31b-abliterated.yaml`      |

After deployment, run guide commands from a directory without a local
`compose.yaml` to use the default user configuration. Before deployment, run
from the repository's `lmserve/` directory. Use `lmserve switch ENTRY`
when another entry is active. Shared setup and lifecycle instructions are in the
[lmserve README](../../README.md).
