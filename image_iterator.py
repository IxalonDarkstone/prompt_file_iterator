import os
import glob as glob_module

import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence

IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "tif")


def _load(path):
    """Load an image file to a ComfyUI-compatible IMAGE tensor and MASK tensor."""
    img     = Image.open(path)
    frames  = []
    masks   = []

    for frame in ImageSequence.Iterator(img):
        frame = ImageOps.exif_transpose(frame)
        if frame.mode == "I":
            frame = frame.point(lambda x: x * (1 / 255))
        rgb = frame.convert("RGB")
        arr = np.array(rgb).astype(np.float32) / 255.0
        frames.append(torch.from_numpy(arr)[None,])          # [1, H, W, 3]

        if "A" in frame.getbands():
            alpha = np.array(frame.getchannel("A")).astype(np.float32) / 255.0
            masks.append(1.0 - torch.from_numpy(alpha).unsqueeze(0))   # [1, H, W]
        else:
            h, w = arr.shape[:2]
            masks.append(torch.zeros((1, h, w), dtype=torch.float32))

    if len(frames) > 1:
        return torch.cat(frames, dim=0), torch.cat(masks, dim=0)
    return frames[0], masks[0]


class ImageIterator:
    """
    Loads image files from a directory in sorted order, returning one per step.
    Outputs a ComfyUI IMAGE tensor — wire it directly into any node that accepts
    images (KSampler, VAEEncode, PreviewImage, etc.).

    cycle_every / step_size work the same as PromptIterator — see that node's
    docstring for the chaining pattern.

    Supported formats: png, jpg, jpeg, webp, gif, bmp, tiff/tif.
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

    RETURN_TYPES  = ("IMAGE",  "MASK",  "STRING",     "INT",        "INT",           "INT")
    RETURN_NAMES  = ("IMAGE",  "MASK",  "image_path", "file_index", "images_found",  "step_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, directory, global_run, cycle_every, start_index):
        return float("nan")

    def iterate(self, directory, global_run, cycle_every, start_index):
        cycle_every = max(1, cycle_every)
        directory   = directory.strip()

        files = []
        for ext in IMAGE_EXTENSIONS:
            files.extend(glob_module.glob(os.path.join(directory, f"*.{ext}")))
            files.extend(glob_module.glob(os.path.join(directory, f"*.{ext.upper()}")))
        files = sorted(set(files))
        total = len(files)

        if total == 0:
            blank = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            mask  = torch.zeros((1, 64, 64),    dtype=torch.float32)
            return (blank, mask, "", 0, 0, cycle_every)

        file_index      = (start_index + global_run // cycle_every) % total
        step_size       = cycle_every * total
        path            = files[file_index]
        image, mask     = _load(path)
        return (image, mask, path, file_index, total, step_size)


NODE_CLASS_MAPPINGS        = {"ImageIterator": ImageIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"ImageIterator": "Image Iterator"}
