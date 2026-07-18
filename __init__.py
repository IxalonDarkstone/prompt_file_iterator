from .prompt_file_iterator  import NODE_CLASS_MAPPINGS as _PFI_C,  NODE_DISPLAY_NAME_MAPPINGS as _PFI_D
from .iteration_controller  import NODE_CLASS_MAPPINGS as _IC_C,   NODE_DISPLAY_NAME_MAPPINGS as _IC_D
from .folder_iterator       import NODE_CLASS_MAPPINGS as _FI_C,   NODE_DISPLAY_NAME_MAPPINGS as _FI_D
from .checkpoint_iterator   import NODE_CLASS_MAPPINGS as _CI_C,   NODE_DISPLAY_NAME_MAPPINGS as _CI_D
from .lora_iterator         import NODE_CLASS_MAPPINGS as _LI_C,   NODE_DISPLAY_NAME_MAPPINGS as _LI_D
from . import server_routes  # noqa: F401  registers /iterator_suite/browse route

NODE_CLASS_MAPPINGS        = {**_PFI_C, **_IC_C, **_FI_C, **_CI_C, **_LI_C}
NODE_DISPLAY_NAME_MAPPINGS = {**_PFI_D, **_IC_D, **_FI_D, **_CI_D, **_LI_D}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
