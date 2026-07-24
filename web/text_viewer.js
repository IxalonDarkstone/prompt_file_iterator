import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "IteratorSuite.TextViewer",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "TextViewer") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            if (this.__itsDisplayWidget) return;

            const { widget } = ComfyWidgets["STRING"](
                this, "displayed_text", ["STRING", { multiline: true }], app
            );
            widget.inputEl.readOnly = true;
            widget.inputEl.style.opacity = 0.7;
            // Populated on each run via onExecuted below — not user input,
            // so it has no reason to occupy a widgets_values slot.
            widget.serialize = false;
            this.__itsDisplayWidget = widget;
        };

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);
            if (!this.__itsDisplayWidget) return;
            this.__itsDisplayWidget.value = message?.text?.[0] ?? "";
        };
    },
});
