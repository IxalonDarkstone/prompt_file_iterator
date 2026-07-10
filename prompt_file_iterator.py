import os
import glob
import json

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

def _load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


class PromptFileIterator:
    """
    Reads .txt files from a directory in sorted order.
    Wire the output STRING into any prompt/text node.
    
    Modes:
      fixed         - always reads the file at the given index widget value
      auto_increment - advances the index automatically on each queue run;
                       use 'Reset Index' button (set index widget then switch
                       back to auto_increment) to restart from a specific point
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "index":     ("INT",    {"default": 0, "min": 0, "max": 99999, "step": 1}),
                "mode":      (["fixed", "auto_increment"],),
                "reset":     ("BOOLEAN", {"default": False, "label_on": "Reset to index", "label_off": "Running"}),
            }
        }

    RETURN_TYPES  = ("STRING", "STRING", "INT", "INT")
    RETURN_NAMES  = ("prompt_text", "image_path", "current_index", "total_files")
    FUNCTION      = "load"
    CATEGORY      = "Prompt Iterator"

    @classmethod
    def IS_CHANGED(cls, directory, index, mode, reset):
        # always re-evaluate so auto_increment advances each run
        if mode == "auto_increment" and not reset:
            return float("nan")
        return False

    def load(self, directory, index, mode, reset):
        directory = directory.strip()
        txt_files = sorted(glob.glob(os.path.join(directory, "*.txt")))
        total = len(txt_files)

        if total == 0:
            return ("No .txt files found in directory.", "", 0, 0)

        state = _load_state()
        key   = directory.replace("\\", "/")

        if mode == "fixed" or reset:
            use_idx = max(0, min(index, total - 1))
            state[key] = use_idx
            _save_state(state)
        else:
            # auto_increment: read current, write next
            current = state.get(key, index)
            use_idx = current % total
            state[key] = (use_idx + 1) % total
            _save_state(state)

        filepath = txt_files[use_idx]

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # find matching image (same basename, any image ext)
        base = os.path.splitext(filepath)[0]
        image_path = ""
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = base + ext
            if os.path.exists(candidate):
                image_path = candidate
                break

        return (text, image_path, use_idx, total)


NODE_CLASS_MAPPINGS        = {"PromptFileIterator": PromptFileIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"PromptFileIterator": "Prompt File Iterator"}
