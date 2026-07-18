import json
import folder_paths
import comfy.sd
import comfy.utils


class LoraIterator:
    """
    Iterates over a user-selected set of LoRAs, applying each one to the
    incoming model and clip and outputting the patched MODEL and CLIP directly.
    Slots are managed by the JS extension (web/model_selector.js) which
    serialises selected names into models_json. If no models are selected,
    all available LoRAs are used.

    cycle_every / step_size: see PromptIterator for the chaining pattern.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model":          ("MODEL",),
                "clip":           ("CLIP",),
                "global_run":     ("INT",   {"forceInput": True}),
                "cycle_every":    ("INT",   {"default": 1, "min": 1, "max": 99999}),
                "models_json":    ("STRING", {"default": "[]"}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip":  ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }

    RETURN_TYPES  = ("MODEL",  "CLIP",  "STRING",    "INT",        "INT",         "INT")
    RETURN_NAMES  = ("model",  "clip",  "lora_name", "file_index", "loras_found", "step_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, model, clip, global_run, cycle_every, strength_model, strength_clip, models_json):
        return float("nan")

    def iterate(self, model, clip, global_run, cycle_every, strength_model, strength_clip, models_json):
        cycle_every = max(1, cycle_every)
        try:
            selected = [m for m in json.loads(models_json) if m]
        except Exception:
            selected = []

        if not selected:
            selected = sorted(folder_paths.get_filename_list("loras"))

        total = len(selected)
        if total == 0:
            raise ValueError("LoraIterator: no LoRAs found")

        file_index = (global_run // cycle_every) % total
        step_size  = cycle_every * total
        lora_name  = selected[file_index]

        lora_path = folder_paths.get_full_path("loras", lora_name)
        if lora_path is None:
            raise ValueError(f"LoraIterator: file not found for {lora_name!r}")

        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
        model_out, clip_out = comfy.sd.load_lora_for_models(
            model, clip, lora, strength_model, strength_clip
        )
        return (model_out, clip_out, lora_name, file_index, total, step_size)


NODE_CLASS_MAPPINGS        = {"LoraIterator": LoraIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"LoraIterator": "LoRA Iterator"}
