# ComfyUI Iterator Suite

A set of ComfyUI custom nodes for multi-dimensional iteration — run every combination of subjects, prompts, checkpoints, and LoRAs without manual reconfiguration.

## Installation

Clone or copy this folder into your ComfyUI `custom_nodes` directory:

```
ComfyUI/custom_nodes/prompt_file_iterator/
```

No additional dependencies are required.

---

## Nodes

All new nodes live in the **Iterators** category. The legacy **Prompt File Iterator** node (category: *Prompt Iterator*) is still available unchanged.

### Iteration Controller

The source of truth for the run counter. Place one per workflow and wire its `global_run` output into every iterator node.

| Input | Type | Description |
|---|---|---|
| `session_name` | STRING | Namespaces the counter — use a unique name per independent workflow |
| `reset` | BOOLEAN | When `true`, resets the counter to 0 and outputs 0 |

| Output | Type | Description |
|---|---|---|
| `global_run` | INT | Current run index (pre-increment); advances by 1 each queue run |

---

### Folder Iterator

Reads files of a given type from a directory, advancing through them based on `global_run` and its position in the dimension chain.

| Input | Type | Description |
|---|---|---|
| `directory` | STRING | Path to the folder |
| `extensions` | STRING | Comma-separated extensions without dots, e.g. `txt` or `png,jpg,jpeg` |
| `global_run` | INT | Wire from Iteration Controller |
| `inner_size` | INT | Product of all faster (inner) dimensions; use `1` for the innermost iterator |

| Output | Type | Description |
|---|---|---|
| `file_path` | STRING | Absolute path to the selected file |
| `file_content` | STRING | File contents for text files; empty for binary files |
| `local_index` | INT | Which file was selected (0-based) |
| `total_files` | INT | Total files found in the directory |
| `outer_size` | INT | Wire into `inner_size` of the next (slower) iterator |

---

### Checkpoint Iterator

Iterates over all checkpoints known to ComfyUI. Wire `model_name` into a **CheckpointLoaderSimple** node.

| Input | Type | Description |
|---|---|---|
| `global_run` | INT | Wire from Iteration Controller |
| `inner_size` | INT | Same chaining role as in Folder Iterator |

| Output | Type | Description |
|---|---|---|
| `model_name` | STRING | Checkpoint filename as returned by ComfyUI |
| `local_index` | INT | |
| `total_models` | INT | |
| `outer_size` | INT | Wire into `inner_size` of the next (slower) iterator |

---

### LoRA Iterator

Same as Checkpoint Iterator but for LoRAs. Wire `lora_name` into a **LoraLoader** node.

Outputs: `lora_name`, `local_index`, `total_loras`, `outer_size`.

---

## How dimension chaining works

Each iterator computes its index as:

```
local_index = (global_run // inner_size) % total_files
outer_size  = inner_size * total_files
```

The **innermost** (fastest-cycling) iterator always uses `inner_size = 1`. Its `outer_size` feeds into the `inner_size` of the next iterator, and so on. The wiring itself defines the iteration order.

**Example — all subjects for each prompt (subjects fast, prompts slow):**

```
[Iteration Controller]  →  global_run
        │
[Folder Iterator]  directory="subjects/"  inner_size=1
        │  file_path → load image node
        │  outer_size=5
        │         │
[Folder Iterator]  directory="prompts/"   inner_size=5
        │  file_content → text node
        │  outer_size=15
        │         │
[Checkpoint Iterator]                     inner_size=15
           model_name → CheckpointLoaderSimple
```

With 5 subjects, 3 prompts, and 2 checkpoints this covers all 30 combinations before cycling. Queue 30 times (or use a repeat node) for a full sweep.

**Resetting mid-sequence:** set `reset = true` on the Iteration Controller, queue once, then set it back to `false`. The next run starts from index 0.

---

## Legacy node

The original **Prompt File Iterator** node is still present and unchanged. It operates independently with its own state and does not interact with the Iteration Controller.

| Output | Description |
|---|---|
| `prompt_text` | Contents of the selected `.txt` file |
| `image_path` | Path to a same-basename image if one exists |
| `current_index` | Zero-based index of the file read |
| `total_files` | Total `.txt` files in the directory |
