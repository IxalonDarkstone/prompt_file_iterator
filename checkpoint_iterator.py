import json
import folder_paths


class CheckpointIterator:
    """
    Iterates over a user-selected set of checkpoints.
    Slots are managed by the JS extension (web/model_selector.js) which
    serialises selected names into models_json. If no models are selected,
    all available checkpoints are used.
    Wire model_name into a CheckpointLoaderSimple node.

    cycle_every / step_size: see PromptIterator for the chaining pattern.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "global_run":  ("INT",    {"forceInput": True}),
                "cycle_every": ("INT",    {"default": 1, "min": 1, "max": 99999}),
                "models_json": ("STRING", {"default": "[]"}),
            }
        }

    RETURN_TYPES  = ("STRING",     "INT",        "INT",           "INT")
    RETURN_NAMES  = ("model_name", "file_index", "models_found",  "step_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, global_run, cycle_every, models_json):
        return float("nan")

    def iterate(self, global_run, cycle_every, models_json):
        cycle_every = max(1, cycle_every)
        try:
            selected = [m for m in json.loads(models_json) if m]
        except Exception:
            selected = []

        if not selected:
            selected = sorted(folder_paths.get_filename_list("checkpoints"))

        total = len(selected)
        if total == 0:
            return ("", 0, 0, cycle_every)

        file_index = (global_run // cycle_every) % total
        step_size  = cycle_every * total
        return (selected[file_index], file_index, total, step_size)


NODE_CLASS_MAPPINGS        = {"CheckpointIterator": CheckpointIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"CheckpointIterator": "Checkpoint Iterator"}
