import folder_paths

_NONE = "None"
_SLOTS = 8


class LoraIterator:
    """
    Iterates over a user-selected set of LoRAs.
    Pick up to 8 LoRAs from the dropdowns; slots left at "None" are skipped.
    If no slots are selected, all available LoRAs are used.
    Wire lora_name into a LoraLoader node.
    See FolderIterator docstring for dimension chaining math.
    """

    @classmethod
    def INPUT_TYPES(cls):
        options = [_NONE] + sorted(folder_paths.get_filename_list("loras"))
        optional = {f"lora_{i}": (options,) for i in range(1, _SLOTS + 1)}
        return {
            "required": {
                "global_run": ("INT", {"forceInput": True}),
                "inner_size": ("INT", {"default": 1, "min": 1, "max": 99999}),
            },
            "optional": optional,
        }

    RETURN_TYPES  = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES  = ("lora_name", "local_index", "total_loras", "outer_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, global_run, inner_size, **kwargs):
        return float("nan")

    def iterate(self, global_run, inner_size, **kwargs):
        inner_size = max(1, inner_size)
        selected   = [
            kwargs[f"lora_{i}"]
            for i in range(1, _SLOTS + 1)
            if kwargs.get(f"lora_{i}", _NONE) != _NONE
        ]
        if not selected:
            selected = sorted(folder_paths.get_filename_list("loras"))

        total = len(selected)
        if total == 0:
            return ("", 0, 0, inner_size)

        local_index = (global_run // inner_size) % total
        outer_size  = inner_size * total
        return (selected[local_index], local_index, total, outer_size)


NODE_CLASS_MAPPINGS        = {"LoraIterator": LoraIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"LoraIterator": "LoRA Iterator"}
