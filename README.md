# ComfyUI Iterator Suite

Custom nodes for running every combination of images, prompts, checkpoints, and LoRAs automatically — without touching the workflow between runs.

## Installation

Clone or copy this folder into your ComfyUI `custom_nodes` directory and restart ComfyUI:

```
ComfyUI/custom_nodes/prompt_file_iterator/
```

---

## The core idea

Every iterator node shares a single counter from the **Iteration Controller**. On each queue run the counter advances by one. Each iterator uses that counter to decide which file or model to use — and because the math is deterministic, every run produces a unique combination.

```
Run 0 → image 0 + prompt 0
Run 1 → image 1 + prompt 0
Run 2 → image 2 + prompt 0
Run 3 → image 0 + prompt 1   ← images cycled, now advance prompt
...
```

You queue exactly as many times as there are combinations, and every combination gets covered.

---

## Quick start: images × prompts

**Scenario:** you have a folder of 3 subject images and a folder of 4 prompts, and you want to generate every combination (12 total).

### Step 1 — place the nodes

Add these nodes to your workflow (all found under the **Iterators** category):

- **Iteration Controller** — 1 instance, sits at the top
- **Image Iterator** — points to your images folder
- **Prompt Iterator** — points to your prompts folder

### Step 2 — wire global_run

Connect the `global_run` output of the Iteration Controller to the `global_run` input of **both** the Image Iterator and the Prompt Iterator.

### Step 3 — set the order

Decide which dimension cycles fastest. If you want to run through all images for each prompt (images fast, prompts slow):

- **Image Iterator:** leave `cycle_every = 1`
- **Prompt Iterator:** connect `step_size` from the Image Iterator → `cycle_every` of the Prompt Iterator

The Image Iterator will report `images_found = 3` and emit `step_size = 3`. Wiring that into the Prompt Iterator's `cycle_every` tells it: *"don't advance until 3 runs have passed."*

### Step 4 — wire content outputs

- `IMAGE` output of Image Iterator → wherever your workflow takes an image (VAEEncode, PreviewImage, etc.)
- `prompt_text` output of Prompt Iterator → your CLIP text encoder

### Step 5 — queue the right number of times

The Prompt Iterator's `step_size` output will equal `3 × 4 = 12`. Queue your workflow 12 times (or use a "Queue N times" button/extension).

**Result:** runs 0–2 use prompt 0 with images 0, 1, 2; runs 3–5 use prompt 1 with images 0, 1, 2; and so on.

---

## Changing the order

To run all prompts for each image instead (prompts fast, images slow):

- **Prompt Iterator:** `cycle_every = 1`
- **Image Iterator:** `cycle_every` ← `step_size` from Prompt Iterator

Nothing else changes. The wiring defines the order.

---

## Adding a third dimension (e.g. checkpoints)

Continuing the example above with 2 checkpoints selected:

```
Image Iterator   cycle_every=1          → step_size=3
Prompt Iterator  cycle_every=3 (←above) → step_size=12
Checkpoint Iter  cycle_every=12 (←above)→ step_size=24
```

Queue 24 times. The checkpoint changes only after all 12 image/prompt combinations finish.

---

## Nodes

### Iteration Controller

| Input | Description |
|---|---|
| `session_name` | Namespaces the counter — use a unique name per independent workflow |
| `reset` | Set to true to reset the counter to 0 on the next run |

| Output | Description |
|---|---|
| `global_run` | Current run index (0-based). Wire to every iterator in the workflow. |

---

### Image Iterator

Loads image files from a folder. Outputs a real image tensor — wire directly into any node that accepts images.

Click **📁 Browse Folder** to navigate to your folder without typing a path.

Supported formats: `png`, `jpg`, `jpeg`, `webp`, `gif`, `bmp`, `tiff`

| Input | Description |
|---|---|
| `directory` | Path to the folder containing images |
| `global_run` | Wire from Iteration Controller |
| `cycle_every` | Advance to next image every N runs. Use 1 for the fastest iterator, or wire `step_size` from a faster iterator. |

| Output | Description |
|---|---|
| `IMAGE` | Loaded image tensor — plug directly into VAEEncode, PreviewImage, etc. |
| `MASK` | Alpha mask (zeros if image has no alpha channel) |
| `image_path` | Full path to the current image file |
| `file_index` | Which image was selected (0-based) |
| `images_found` | Total images discovered in the folder |
| `step_size` | Wire into `cycle_every` of the next (slower) iterator |

---

### Prompt Iterator

Reads `.txt` files from a folder, one per step.

Click **📁 Browse Folder** to navigate to your folder.

| Input | Description |
|---|---|
| `directory` | Path to the folder containing `.txt` files |
| `global_run` | Wire from Iteration Controller |
| `cycle_every` | Same role as in Image Iterator |

| Output | Description |
|---|---|
| `prompt_text` | Contents of the current `.txt` file |
| `file_index` | Which file was selected (0-based) |
| `prompts_found` | Total `.txt` files in the folder |
| `step_size` | Wire into `cycle_every` of the next (slower) iterator |

---

### Checkpoint Iterator

Iterates over a selected list of ComfyUI checkpoints. Click **+ Add Checkpoint** to add slots; click **✕** to remove one. If no checkpoints are selected, all available checkpoints are used.

Wire `model_name` into a **CheckpointLoaderSimple** node.

| Input | Description |
|---|---|
| `global_run` | Wire from Iteration Controller |
| `cycle_every` | Same role as in Image Iterator |

| Output | Description |
|---|---|
| `model_name` | Checkpoint filename |
| `file_index` | Which checkpoint was selected (0-based) |
| `models_found` | Number of checkpoints in the active list |
| `step_size` | Wire into `cycle_every` of the next (slower) iterator |

---

### LoRA Iterator

Same as Checkpoint Iterator but for LoRAs. Wire `lora_name` into a **LoraLoader** node.

---

## Common patterns

| Goal | Fast dimension | Slow dimension |
|---|---|---|
| All images per prompt | Image Iterator (`cycle_every=1`) | Prompt Iterator |
| All prompts per image | Prompt Iterator (`cycle_every=1`) | Image Iterator |
| Test every checkpoint on one prompt+image | Image or Prompt Iterator | Checkpoint Iterator |
| Full grid: images × prompts × checkpoints | Image → Prompt → Checkpoint | ← slowest |

---

## Legacy node

The original **Prompt File Iterator** (category: *Prompt Iterator*) is still present and unchanged for backwards compatibility. It operates independently and does not interact with the Iteration Controller.
