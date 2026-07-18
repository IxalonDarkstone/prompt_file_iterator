# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A ComfyUI custom node that reads `.txt` prompt files from a directory in sorted order and returns one per queue run. It is installed by placing (or symlinking) this folder inside ComfyUI's `custom_nodes/` directory.

## How the node works

`PromptFileIterator` in `prompt_file_iterator.py` is the only node. It exposes four outputs:

| Output | Type | Description |
|---|---|---|
| `prompt_text` | STRING | Contents of the selected `.txt` file |
| `image_path` | STRING | Path to a same-basename image (`.png/.jpg/.jpeg/.webp`) if one exists |
| `current_index` | INT | Zero-based index of the file that was read |
| `total_files` | INT | Total number of `.txt` files found |

**Modes:**
- `fixed` — always reads the file at the `index` widget value; writes that index to `state.json`
- `auto_increment` — reads the current persisted index for the directory, then writes `(current + 1) % total` so the next run advances automatically

**Reset:** setting the `reset` input to `True` forces `fixed` behaviour (writes `index` to state) even when `mode` is `auto_increment`, allowing restart from a specific point.

## State persistence

`state.json` lives next to `prompt_file_iterator.py` and is keyed by directory path (backslashes normalised to `/`). It is written on every `load()` call. There is no locking — concurrent ComfyUI queue runs could race.

## ComfyUI integration points

`__init__.py` exports `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`, which ComfyUI discovers automatically. `IS_CHANGED` returns `float("nan")` for `auto_increment` mode to force re-execution every queue run; it returns `False` otherwise so ComfyUI can cache.

## No build or test setup

There are no dependencies beyond the Python standard library (`os`, `glob`, `json`). There is no test suite, linter config, or build step.
