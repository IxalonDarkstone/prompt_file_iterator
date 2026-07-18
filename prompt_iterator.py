import os
import glob as glob_module


class PromptIterator:
    """
    Reads .txt files from a directory in sorted order, returning one per step.

    cycle_every: how many global runs before this iterator advances.
      - Set to 1 if this is the fastest (innermost) dimension.
      - Wire step_size from a faster iterator into cycle_every to make this
        iterator advance only after the faster one completes a full cycle.

    step_size output: wire this into the cycle_every of the next (slower)
      iterator, or use it to know how many total queue runs are needed.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory":   ("STRING", {"default": ""}),
                "global_run":  ("INT",    {"forceInput": True}),
                "cycle_every": ("INT",    {"default": 1, "min": 1, "max": 99999}),
                "start_index": ("INT",    {"default": 0, "min": 0, "max": 99999}),
            }
        }

    RETURN_TYPES  = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES  = ("prompt_text", "file_index", "prompts_found", "step_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, directory, global_run, cycle_every, start_index):
        return float("nan")

    def iterate(self, directory, global_run, cycle_every, start_index):
        cycle_every = max(1, cycle_every)
        files       = sorted(glob_module.glob(os.path.join(directory.strip(), "*.txt")))
        total       = len(files)

        if total == 0:
            return ("", 0, 0, cycle_every)

        file_index = (start_index + global_run // cycle_every) % total
        step_size  = cycle_every * total

        with open(files[file_index], "r", encoding="utf-8") as f:
            text = f.read().strip()

        return (text, file_index, total, step_size)


NODE_CLASS_MAPPINGS        = {"PromptIterator": PromptIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"PromptIterator": "Prompt Iterator"}
