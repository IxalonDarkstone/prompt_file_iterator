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

## No build or test setup

No dependencies beyond the Python standard library and ComfyUI's built-in `folder_paths`. No test suite, linter config, or build step.
