import folder_paths

_NONE = "None"
_SLOTS = 8


class CheckpointIterator:
    """
    Iterates over a user-selected set of checkpoints.
    Pick up to 8 models from the dropdowns; slots left at "None" are skipped.
    If no slots are selected, all available checkpoints are used.
    Wire model_name into a CheckpointLoaderSimple node.
    See FolderIterator docstring for dimension chaining math.
    """

    @classmethod
    def INPUT_TYPES(cls):
        options = [_NONE] + sorted(folder_paths.get_filename_list("checkpoints"))
        optional = {f"model_{i}": (options,) for i in range(1, _SLOTS + 1)}
        return {
            "required": {
                "global_run": ("INT", {"forceInput": True}),
                "inner_size": ("INT", {"default": 1, "min": 1, "max": 99999}),
            },
            "optional": optional,
        }

    RETURN_TYPES  = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES  = ("model_name", "local_index", "total_models", "outer_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, global_run, inner_size, **kwargs):
        return float("nan")

    def iterate(self, global_run, inner_size, **kwargs):
        inner_size = max(1, inner_size)
        selected   = [
            kwargs[f"model_{i}"]
            for i in range(1, _SLOTS + 1)
            if kwargs.get(f"model_{i}", _NONE) != _NONE
        ]
        if not selected:
            selected = sorted(folder_paths.get_filename_list("checkpoints"))

        total = len(selected)
        if total == 0:
            return ("", 0, 0, inner_size)

        local_index = (global_run // inner_size) % total
        outer_size  = inner_size * total
        return (selected[local_index], local_index, total, outer_size)


NODE_CLASS_MAPPINGS        = {"CheckpointIterator": CheckpointIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"CheckpointIterator": "Checkpoint Iterator"}
