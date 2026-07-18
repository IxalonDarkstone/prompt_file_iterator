import folder_paths


class CheckpointIterator:
    """
    Iterates over available ComfyUI checkpoints.
    Wire model_name into a CheckpointLoaderSimple node.
    See FolderIterator docstring for dimension chaining math.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "global_run": ("INT", {"forceInput": True}),
                "inner_size": ("INT", {"default": 1, "min": 1, "max": 99999}),
            }
        }

    RETURN_TYPES  = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES  = ("model_name", "local_index", "total_models", "outer_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, global_run, inner_size):
        return float("nan")

    def iterate(self, global_run, inner_size):
        inner_size = max(1, inner_size)
        models     = sorted(folder_paths.get_filename_list("checkpoints"))
        total      = len(models)

        if total == 0:
            return ("", 0, 0, inner_size)

        local_index = (global_run // inner_size) % total
        outer_size  = inner_size * total
        return (models[local_index], local_index, total, outer_size)


NODE_CLASS_MAPPINGS        = {"CheckpointIterator": CheckpointIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"CheckpointIterator": "Checkpoint Iterator"}
