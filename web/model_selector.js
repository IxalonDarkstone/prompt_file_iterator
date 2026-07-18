import { app } from "../../scripts/app.js";

// ---------------------------------------------------------------------------
// Configuration: one entry per node type that uses dynamic model slots
// ---------------------------------------------------------------------------

const MODEL_NODES = [
    { nodeName: "CheckpointIterator", modelType: "checkpoints", addLabel: "+ Add Checkpoint" },
    { nodeName: "LoraIterator",       modelType: "loras",       addLabel: "+ Add LoRA"       },
];

const SLOT_PREFIX  = "its_slot_";
const ADD_BTN_NAME = "its_add";
const MARGIN       = 6;
const REMOVE_W     = 28;
const GAP          = 4;

// ---------------------------------------------------------------------------
// Model list — fetched once per type, shared across all nodes of that type
// ---------------------------------------------------------------------------

const modelCache = {};

async function fetchModels(type) {
    if (modelCache[type]) return modelCache[type];
    try {
        const res = await fetch(`/iterator_suite/models?type=${encodeURIComponent(type)}`);
        const data = await res.json();
        modelCache[type] = data.models ?? [];
    } catch {
        modelCache[type] = [];
    }
    return modelCache[type];
}

// ---------------------------------------------------------------------------
// Register one ComfyUI extension per node type
// ---------------------------------------------------------------------------

for (const cfg of MODEL_NODES) {
    registerExtension(cfg);
}

function registerExtension({ nodeName, modelType, addLabel }) {
    // Start loading immediately so the list is ready before the user clicks
    let options = [];
    fetchModels(modelType).then(m => { options = m; });
    const getOptions = () => options;

    app.registerExtension({
        name: `IteratorSuite.${nodeName}`,

        async beforeRegisterNodeDef(nodeType, nodeData) {
            if (nodeData.name !== nodeName) return;

            // New node created from the menu
            const origOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                origOnNodeCreated?.apply(this, arguments);
                setupNode(this, getOptions, addLabel);
            };

            // Node loaded from a saved workflow
            const origOnConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function (info) {
                origOnConfigure?.apply(this, arguments);
                restoreSlots(this, getOptions, addLabel);
            };
        },
    });
}

// ---------------------------------------------------------------------------
// Node setup
// ---------------------------------------------------------------------------

function setupNode(node, getOptions, addLabel) {
    hideJsonWidget(node);

    node.addWidget("button", addLabel, ADD_BTN_NAME, () => {
        const opts = getOptions();
        addSlot(node, getOptions, opts[0] ?? "");
        node.setSize(node.computeSize());
        app.graph.setDirtyCanvas(true, true);
    });
}

function hideJsonWidget(node) {
    const w = jsonWidget(node);
    if (!w) return;
    w.computeSize = () => [0, -4];
    w.draw        = () => {};
}

function restoreSlots(node, getOptions, addLabel) {
    const jw = jsonWidget(node);
    if (!jw) return;

    let saved;
    try { saved = JSON.parse(jw.value ?? "[]"); }
    catch { return; }
    if (!Array.isArray(saved) || !saved.length) return;

    // Remove any slots that may already exist (shouldn't, but be safe)
    node.widgets = node.widgets.filter(w => !w.name?.startsWith(SLOT_PREFIX));

    for (const val of saved) {
        addSlot(node, getOptions, val);
    }
    node.setSize(node.computeSize());
}

// ---------------------------------------------------------------------------
// Slot management
// ---------------------------------------------------------------------------

function addSlot(node, getOptions, defaultValue) {
    const addIdx  = node.widgets.findIndex(w => w.name === ADD_BTN_NAME);
    const slotName = `${SLOT_PREFIX}${Date.now()}`;

    const slot = makeSlotWidget(slotName, defaultValue, getOptions,
        /* onChange */ () => {
            syncJson(node);
            app.graph.setDirtyCanvas(true, true);
        },
        /* onRemove */ () => {
            node.widgets = node.widgets.filter(w => w !== slot);
            syncJson(node);
            node.setSize(node.computeSize());
            app.graph.setDirtyCanvas(true, true);
        }
    );

    const insertAt = addIdx === -1 ? node.widgets.length : addIdx;
    node.widgets.splice(insertAt, 0, slot);
    syncJson(node);
}

function syncJson(node) {
    const jw = jsonWidget(node);
    if (!jw) return;
    jw.value = JSON.stringify(
        node.widgets
            .filter(w => w.name?.startsWith(SLOT_PREFIX))
            .map(w => w.value)
    );
}

function jsonWidget(node) {
    return node.widgets?.find(w => w.name === "models_json") ?? null;
}

// ---------------------------------------------------------------------------
// Custom slot widget — rendered on the LiteGraph canvas
// ---------------------------------------------------------------------------

function makeSlotWidget(name, defaultValue, getOptions, onChange, onRemove) {
    const H = LiteGraph.NODE_WIDGET_HEIGHT ?? 20;

    const widget = {
        type:        "model_slot",
        name,
        value:       defaultValue,
        serialize:   false,          // serialised indirectly via models_json
        computeSize: (w) => [w, H],

        draw(ctx, node, width, posY) {
            const dropW = Math.max(20, width - 2 * MARGIN - REMOVE_W - GAP);
            const btnX  = MARGIN + dropW + GAP;

            // Dropdown background
            ctx.fillStyle   = "#222";
            ctx.strokeStyle = "#555";
            ctx.lineWidth   = 1;
            ctx.beginPath();
            ctx.roundRect(MARGIN, posY + 1, dropW, H - 2, 4);
            ctx.fill();
            ctx.stroke();

            // Value text (clipped so it doesn't overflow into the arrow)
            ctx.save();
            ctx.beginPath();
            ctx.rect(MARGIN + 4, posY, dropW - 18, H);
            ctx.clip();
            ctx.fillStyle    = "#ddd";
            ctx.font         = `${Math.round(H * 0.55)}px sans-serif`;
            ctx.textAlign    = "left";
            ctx.textBaseline = "middle";
            ctx.fillText(this.value || "(none)", MARGIN + 6, posY + H / 2);
            ctx.restore();

            // Dropdown arrow
            ctx.fillStyle    = "#888";
            ctx.font         = "12px sans-serif";
            ctx.textAlign    = "right";
            ctx.textBaseline = "middle";
            ctx.fillText("▾", MARGIN + dropW - 4, posY + H / 2);

            // Remove button
            ctx.fillStyle   = "#4a1818";
            ctx.strokeStyle = "#833";
            ctx.beginPath();
            ctx.roundRect(btnX, posY + 1, REMOVE_W, H - 2, 4);
            ctx.fill();
            ctx.stroke();
            ctx.fillStyle    = "#e88";
            ctx.textAlign    = "center";
            ctx.fillText("✕", btnX + REMOVE_W / 2, posY + H / 2);
        },

        mouse(e, pos, node) {
            if (e.type !== "pointerdown" && e.type !== "mousedown") return false;

            const dropW = Math.max(20, node.size[0] - 2 * MARGIN - REMOVE_W - GAP);
            const btnX  = MARGIN + dropW + GAP;

            if (pos[0] >= btnX) {
                onRemove();
                return true;
            }

            // Show a context menu of available models
            const opts = getOptions();
            if (!opts.length) return true;   // not loaded yet — ignore click

            new LiteGraph.ContextMenu(
                opts,
                {
                    scale:     Math.max(1, app.canvas.ds?.scale ?? 1),
                    event:     e,
                    className: "dark",
                    callback:  (v) => {
                        widget.value = v;
                        onChange();
                        app.graph.setDirtyCanvas(true);
                    },
                },
                app.canvas.getCanvasWindow?.() ?? window
            );
            return true;
        },
    };

    return widget;
}
