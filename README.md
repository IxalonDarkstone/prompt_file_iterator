# Prompt File Iterator

A ComfyUI custom node that reads `.txt` prompt files from a directory in sorted order, returning one file's content per queue run.

## Installation

Clone or copy this folder into your ComfyUI `custom_nodes` directory:

```
ComfyUI/custom_nodes/prompt_file_iterator/
```

No additional dependencies are required.

## Usage

Add the **Prompt File Iterator** node (found under the *Prompt Iterator* category) to your workflow and wire its `prompt_text` output into any text/prompt node.

### Inputs

| Input | Type | Description |
|---|---|---|
| `directory` | STRING | Path to the folder containing `.txt` files |
| `index` | INT | File index to use in `fixed` mode, or the starting index for `auto_increment` |
| `mode` | ENUM | `fixed` or `auto_increment` (see below) |
| `reset` | BOOLEAN | When `true`, forces the index back to the `index` widget value |

### Outputs

| Output | Type | Description |
|---|---|---|
| `prompt_text` | STRING | Contents of the selected `.txt` file |
| `image_path` | STRING | Path to a same-basename image (`.png`, `.jpg`, `.jpeg`, `.webp`) if one exists alongside the `.txt` file |
| `current_index` | INT | Zero-based index of the file that was read |
| `total_files` | INT | Total number of `.txt` files found in the directory |

### Modes

- **`fixed`** — always reads the file at the `index` widget value. Useful for manually stepping through files.
- **`auto_increment`** — advances the index automatically on each queue run, cycling back to 0 after the last file.

### Resetting the index

Set `reset` to `true` to jump back to the current `index` value on the next run. Switch `reset` back to `false` (or leave `mode` as `fixed`) to resume normal operation from that point.

## File pairing

If a `.txt` file has a matching image with the same base name in the same directory, `image_path` will contain its path. This is useful for workflows that pair a prompt with a reference image.

```
prompts/
  001.txt   ← prompt_text
  001.png   ← image_path
  002.txt
  002.jpg
```
