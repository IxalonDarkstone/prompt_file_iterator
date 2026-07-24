class TextViewer:
    """
    Displays incoming text in a scrollable, read-only textbox on the node.
    Wire the file_list output from PromptIterator/ImageIterator into this
    to see every discovered file listed by index — handy for picking a
    start_index. Works with any STRING output, not just file_list.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION     = "show"
    CATEGORY     = "Iterators"
    OUTPUT_NODE  = True

    def show(self, text):
        return {"ui": {"text": [text]}}


NODE_CLASS_MAPPINGS        = {"TextViewer": TextViewer}
NODE_DISPLAY_NAME_MAPPINGS = {"TextViewer": "Text Viewer"}
