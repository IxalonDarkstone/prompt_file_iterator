# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A ComfyUI custom node pack providing multi-dimensional iteration over files, checkpoints, and LoRAs. Installed by placing (or symlinking) this folder inside ComfyUI's `custom_nodes/` directory.

## Node inventory

| File | Node class | Display name | Category |
|---|---|---|---|
| `prompt_file_iterator.py` | `PromptFileIterator` | Prompt File Iterator | Prompt Iterator |
| `iteration_controller.py` | `IterationController` | Iteration Controller | Iterators |
| `folder_iterator.py` | `FolderIterator` | Folder Iterator | Iterators |
| `checkpoint_iterator.py` | `CheckpointIterator` | Checkpoint Iterator | Iterators |
| `lora_iterator.py` | `LoraIterator` | LoRA Iterator | Iterators |

`__init__.py` merges all five `NODE_CLASS_MAPPINGS` dicts. `state.py` provides shared `load_state`/`save_state` helpers used only by `IterationController`.

## Dimension chaining math

The core invariant across all new iterator nodes:

```
local_index = (global_run // inner_size) % total
outer_size  = inner_size * total
```

`outer_size` from an inner (faster) iterator feeds into `inner_size` of the next outer (slower) one. The innermost iterator always has `inner_size=1`. This is how iteration order is encoded in the wiring, not in any config.

## State persistence

`state.json` sits next to `__init__.py` and is the single shared store. Key namespaces:

- Legacy `PromptFileIterator` uses bare directory paths (e.g. `"C:/prompts/set1"`) — managed by private helpers inside `prompt_file_iterator.py`
- `IterationController` uses `"session:{session_name}"` keys — managed by `state.py`

These namespaces cannot collide. There is no locking; concurrent ComfyUI queue runs could race.

## IS_CHANGED behaviour

All new nodes return `float("nan")` unconditionally so ComfyUI always re-executes them. `PromptFileIterator` returns `nan` only in `auto_increment` mode — this is intentional and must not change.

## ComfyUI-specific imports

`checkpoint_iterator.py` and `lora_iterator.py` import `folder_paths` at module level. This module is part of ComfyUI's runtime and is not available outside it — these files will fail to import in plain Python. Do not add a try/except guard; a loud failure is correct outside ComfyUI.

## Backwards compatibility constraint

`prompt_file_iterator.py` must never be modified. It is a stable public API; users may have workflows depending on the exact `PromptFileIterator` node name and output signature.

## Frontend extension

`WEB_DIRECTORY = "./web"` in `__init__.py` tells ComfyUI to auto-load all `.js` files from `web/`. Currently:

- `web/folder_picker.js` — adds a "Browse Folder" button to `FolderIterator` nodes. Calls `GET /iterator_suite/browse?path=...` (registered in `server_routes.py`) which returns `{path, parent, dirs:[{name,path}]}`. On Windows with no path, returns drive letters. The dialog handles Escape and backdrop-click to close.

`server_routes.py` registers the aiohttp route using `PromptServer.instance.routes`. The whole file is wrapped in `try/except` so it silently does nothing outside ComfyUI.

## Checkpoint / LoRA multi-select

`CheckpointIterator` and `LoraIterator` expose 8 optional COMBO inputs (`model_1`…`model_8` / `lora_1`…`lora_8`). Slots left at `"None"` are filtered out; the remaining selections form the iteration list. If all slots are `"None"`, the node falls back to iterating all available models. `_SLOTS = 8` at the top of each file controls the count.

## No build or test setup

No dependencies beyond the Python standard library and ComfyUI's built-in `folder_paths`. No test suite, linter config, or build step.
