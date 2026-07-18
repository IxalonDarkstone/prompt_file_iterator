from .state import load_state, save_state


class IterationController:
    """
    Global run counter. Wire global_run into every iterator node in the workflow.
    Each queue run outputs the current counter then increments it.
    Use a unique session_name per independent workflow to avoid counter collisions.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "session_name": ("STRING",  {"default": "default"}),
                "reset":        ("BOOLEAN", {"default": False, "label_on": "Reset", "label_off": "Running"}),
            }
        }

    RETURN_TYPES  = ("INT",)
    RETURN_NAMES  = ("global_run",)
    FUNCTION      = "run"
    CATEGORY      = "Iterators"

    @classmethod
    def IS_CHANGED(cls, session_name, reset):
        return float("nan")

    def run(self, session_name, reset):
        state = load_state()
        key   = f"session:{session_name}"

        if reset:
            state[key] = 0
            save_state(state)
            return (0,)

        current     = state.get(key, 0)
        state[key]  = current + 1
        save_state(state)
        return (current,)


NODE_CLASS_MAPPINGS        = {"IterationController": IterationController}
NODE_DISPLAY_NAME_MAPPINGS = {"IterationController": "Iteration Controller"}
