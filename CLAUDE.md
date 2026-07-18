# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A ComfyUI custom node pack for multi-dimensional iteration over images, prompts, checkpoints, and LoRAs. Installed by placing (or symlinking) this folder inside ComfyUI's `custom_nodes/` directory.

## Node inventory

| File | Node class | Display name | Category |
|---|---|---|---|
| `prompt_file_iterator.py` | `PromptFileIterator` | Prompt File Iterator | Prompt Iterator |
| `iteration_controller.py` | `IterationController` | Iteration Controller | Iterators |
| `prompt_iterator.py` | `PromptIterator` | Prompt Iterator | Iterators |
| `image_iterator.py` | `ImageIterator` | Image Iterator | Iterators |
| `checkpoint_iterator.py` | `CheckpointIterator` | Checkpoint Iterator | Iterators |
| `lora_iterator.py` | `LoraIterator` | LoRA Iterator | Iterators |

`__init__.py` merges all mappings and sets `WEB_DIRECTORY = "./web"`.
`state.py` provides shared `load_state`/`save_state` used only by `IterationController`.

## Dimension chaining math

All iterator nodes share this invariant:

```
file_index = (global_run // cycle_every) % total_files
step_size  = cycle_every * total_files
```

`step_size` from the faster (inner) iterator feeds into `cycle_every` of the next slower (outer) iterator. The innermost iterator always uses `cycle_every=1`. The outermost iterator's `step_size` equals the total runs needed (product of all dimension sizes).

## State persistence

`state.json` sits next to `__init__.py`. Key namespaces:
- `PromptFileIterator` (legacy): bare directory paths
- `IterationController`: `"session:{session_name}"`

No locking — concurrent queue runs can race.

## IS_CHANGED

All new nodes return `float("nan")` unconditionally. `PromptFileIterator` returns `nan` only in `auto_increment` mode — do not change this.

## Image loading

`image_iterator.py` loads images with PIL/Pillow, matching ComfyUI's LoadImage output format exactly:
- `IMAGE`: float32 tensor `[B, H, W, 3]`, values in `[0, 1]`
- `MASK`: float32 tensor `[B, H, W]`, `1.0 - alpha/255`
- Multi-frame images (animated GIFs) produce batch tensors

PIL, NumPy, and Torch are always available in ComfyUI's Python environment.

## Frontend extension

`WEB_DIRECTORY = "./web"` auto-loads all `.js` files:

- `web/folder_picker.js` — adds a Browse button to `PromptIterator` and `ImageIterator` nodes. Calls `GET /iterator_suite/browse?path=...` (returns `{path, parent, dirs:[{name,path}]}`). Windows-aware: no path → returns drive letters.
- `web/model_selector.js` — adds dynamic `+ Add` / `✕` slot widgets to `CheckpointIterator` and `LoraIterator`. Each node has a hidden `models_json` STRING widget (zero-height draw override) that stores the JSON-serialised list of selected model names. Slots use `LiteGraph.ContextMenu` for dropdowns and are restored from `models_json` on workflow load via `onConfigure`.

## Backwards compatibility constraint

`prompt_file_iterator.py` must never be modified. It is a stable public API.

## No build or test setup

No dependencies beyond Python stdlib, PIL/Pillow, NumPy, Torch, and ComfyUI's built-in `folder_paths`. No test suite, linter config, or build step.
