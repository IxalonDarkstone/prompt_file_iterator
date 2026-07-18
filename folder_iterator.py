import os
import glob as glob_module


class FolderIterator:
    """
    Reads files from a directory, advancing through them based on global_run.

    Dimension math:
      local_index = (global_run // inner_size) % total_files
      outer_size  = inner_size * total_files

    Chain outer_size into the inner_size of the next (slower) iterator to
    define iteration order. The fastest (innermost) iterator uses inner_size=1.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory":  ("STRING", {"default": ""}),
                "extensions": ("STRING", {"default": "txt"}),
                "global_run": ("INT",    {"forceInput": True}),
                "inner_size": ("INT",    {"default": 1, "min": 1, "max": 99999}),
            }
        }

    RETURN_TYPES  = ("STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES  = ("file_path", "file_content", "local_index", "total_files", "outer_size")
    FUNCTION      = "iterate"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, directory, extensions, global_run, inner_size):
        return float("nan")

    def iterate(self, directory, extensions, global_run, inner_size):
        inner_size = max(1, inner_size)
        directory  = directory.strip()
        exts       = [e.strip().lstrip(".").lower() for e in extensions.split(",") if e.strip()]

        files = []
        for ext in exts:
            files.extend(glob_module.glob(os.path.join(directory, f"*.{ext}")))
        files = sorted(set(files))
        total = len(files)

        if total == 0:
            return ("", "", 0, 0, inner_size)

        local_index = (global_run // inner_size) % total
        outer_size  = inner_size * total
        file_path   = files[local_index]

        file_content = ""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except (UnicodeDecodeError, OSError):
            pass

        return (file_path, file_content, local_index, total, outer_size)


NODE_CLASS_MAPPINGS        = {"FolderIterator": FolderIterator}
NODE_DISPLAY_NAME_MAPPINGS = {"FolderIterator": "Folder Iterator"}
