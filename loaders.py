import folder_paths
import comfy.sd
import comfy.utils


class CheckpointLoaderFromString:
    """
    Loads a checkpoint given its filename as a plain STRING.
    Wire model_name from CheckpointIterator here; use model/clip/vae outputs
    exactly as you would from a CheckpointLoaderSimple node.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES  = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES  = ("model",  "clip",  "vae")
    FUNCTION      = "load"
    CATEGORY      = "Iterators"

    def load(self, model_name):
        ckpt_path = folder_paths.get_full_path("checkpoints", model_name)
        if ckpt_path is None:
            raise ValueError(f"Checkpoint not found: {model_name!r}")
        out = comfy.sd.load_checkpoint_guess_config(
            ckpt_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=folder_paths.get_folder_paths("embeddings"),
        )
        return out[:3]


class LoraLoaderFromString:
    """
    Applies a LoRA given its filename as a plain STRING.
    Wire lora_name from LoraIterator here. Chain multiple instances to stack LoRAs.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model":          ("MODEL",),
                "clip":           ("CLIP",),
                "lora_name":      ("STRING", {"forceInput": True}),
                "strength_model": ("FLOAT",  {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip":  ("FLOAT",  {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }

    RETURN_TYPES  = ("MODEL", "CLIP")
    RETURN_NAMES  = ("model",  "clip")
    FUNCTION      = "load"
    CATEGORY      = "Iterators"

    def load(self, model, clip, lora_name, strength_model, strength_clip):
        lora_path = folder_paths.get_full_path("loras", lora_name)
        if lora_path is None:
            raise ValueError(f"LoRA not found: {lora_name!r}")
        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
        model_out, clip_out = comfy.sd.load_lora_for_models(
            model, clip, lora, strength_model, strength_clip
        )
        return (model_out, clip_out)


NODE_CLASS_MAPPINGS = {
    "CheckpointLoaderFromString": CheckpointLoaderFromString,
    "LoraLoaderFromString":       LoraLoaderFromString,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckpointLoaderFromString": "Checkpoint Loader (from String)",
    "LoraLoaderFromString":       "LoRA Loader (from String)",
}
