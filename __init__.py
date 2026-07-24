from .prompt_file_iterator  import NODE_CLASS_MAPPINGS as _PFI_C,  NODE_DISPLAY_NAME_MAPPINGS as _PFI_D
from .iteration_controller  import NODE_CLASS_MAPPINGS as _IC_C,   NODE_DISPLAY_NAME_MAPPINGS as _IC_D
from .prompt_iterator       import NODE_CLASS_MAPPINGS as _PI_C,   NODE_DISPLAY_NAME_MAPPINGS as _PI_D
from .image_iterator        import NODE_CLASS_MAPPINGS as _II_C,   NODE_DISPLAY_NAME_MAPPINGS as _II_D
from .checkpoint_iterator   import NODE_CLASS_MAPPINGS as _CI_C,   NODE_DISPLAY_NAME_MAPPINGS as _CI_D
from .lora_iterator         import NODE_CLASS_MAPPINGS as _LI_C,   NODE_DISPLAY_NAME_MAPPINGS as _LI_D
from .loaders               import NODE_CLASS_MAPPINGS as _LO_C,   NODE_DISPLAY_NAME_MAPPINGS as _LO_D
from .text_viewer           import NODE_CLASS_MAPPINGS as _TV_C,   NODE_DISPLAY_NAME_MAPPINGS as _TV_D
from . import server_routes  # noqa: F401  registers /iterator_suite/* routes

NODE_CLASS_MAPPINGS        = {**_PFI_C, **_IC_C, **_PI_C, **_II_C, **_CI_C, **_LI_C, **_LO_C, **_TV_C}
NODE_DISPLAY_NAME_MAPPINGS = {**_PFI_D, **_IC_D, **_PI_D, **_II_D, **_CI_D, **_LI_D, **_LO_D, **_TV_D}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
