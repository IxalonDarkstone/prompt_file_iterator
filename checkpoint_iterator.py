import json
import folder_paths
import comfy.sd


class CheckpointIterator:
    """
    Iterates over a user-selected set of checkpoints, loading each one and
    outputting MODEL/CLIP/VAE directly. Slots are managed by the JS extension
    (web/model_selector.js) which serialises selected names into models_json.
    If no models are selected, all available checkpoints are used.

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

    RETURN_TYPES  = ("MODEL",  "CLIP",  "VAE",  "STRING",     "INT",        "INT",          "INT")
    RETURN_NAMES  = ("model",  "clip",  "vae",  "model_name", "file_index", "models_found", "step_size")
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
            ckpts = folder_paths.get_filename_list("checkpoints")
            try:
                diff = folder_paths.get_filename_list("diffusion_models")
            except Exception:
                diff = []
            selected = sorted(set(ckpts) | set(diff))

        total = len(selected)
        if total == 0:
            raise ValueError("CheckpointIterator: no checkpoints found")

        file_index = (global_run // cycle_every) % total
        step_size  = cycle_every * total
        model_name = selected[file_index]

        ckpt_path = folder_paths.get_full_path("checkpoints", model_name)
        if ckpt_path is None:
            ckpt_path = folder_paths.get_full_path("diffusion_models", model_name)
        if ckpt_path is None:
            raise ValueError(f"CheckpointIterator: file not found for {model_name!r}")

        out = comfy.sd.load_checkpoint_guess_config(
            ckpt_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=folder_paths.get_folder_paths("embeddings"),
        )
        model, clip, vae = out[0], out[1], out[2]
        return (model, clip, vae, model_name, file_index, total, step_size)


NODE_CLASS_MAPPINGS        = {"CheckpointIterator": CheckpointIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"CheckpointIterator": "Checkpoint Iterator"}
