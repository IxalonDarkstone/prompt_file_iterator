import folder_paths


class LoraIterator:
    """
    Iterates over available ComfyUI LoRAs.
    Wire lora_name into a LoraLoader node.
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
    RETURN_NAMES  = ("lora_name", "local_index", "total_loras", "outer_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, global_run, inner_size):
        return float("nan")

    def iterate(self, global_run, inner_size):
        inner_size = max(1, inner_size)
        loras      = sorted(folder_paths.get_filename_list("loras"))
        total      = len(loras)

        if total == 0:
            return ("", 0, 0, inner_size)

        local_index = (global_run // inner_size) % total
        outer_size  = inner_size * total
        return (loras[local_index], local_index, total, outer_size)


NODE_CLASS_MAPPINGS        = {"LoraIterator": LoraIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"LoraIterator": "LoRA Iterator"}
