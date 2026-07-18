import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "IteratorSuite.FolderPicker",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        const FOLDER_NODES = new Set(["PromptIterator", "ImageIterator"]);
        if (!FOLDER_NODES.has(nodeData.name)) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const dirWidget = this.widgets?.find(w => w.name === "directory");
            if (!dirWidget) return;

            this.addWidget("button", "📁  Browse Folder", "browse", () => {
                openFolderPicker(dirWidget.value ?? "", (selectedPath) => {
                    dirWidget.value = selectedPath;
                    app.graph.setDirtyCanvas(true);
                });
            });
        };
    },
});

// ---------------------------------------------------------------------------
// Backend call
// ---------------------------------------------------------------------------

async function fetchDir(path) {
    const url = "/iterator_suite/browse" +
        (path ? `?path=${encodeURIComponent(path)}` : "");
    const res = await fetch(url);
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error ?? `HTTP ${res.status}`);
    }
    return res.json();
}

// ---------------------------------------------------------------------------
// Folder picker dialog
// ---------------------------------------------------------------------------

function openFolderPicker(startPath, onSelect) {
    document.getElementById("its-folder-picker")?.remove();

    // --- overlay ---
    const overlay = el("div", {
        id: "its-folder-picker",
        style: css({
            position: "fixed", inset: "0", background: "rgba(0,0,0,0.75)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: "10000",
        }),
    });

    // --- dialog ---
    const dialog = el("div", {
        style: css({
            background: "#1e1e1e", border: "1px solid #555", borderRadius: "8px",
            padding: "16px", width: "520px", maxHeight: "70vh",
            display: "flex", flexDirection: "column", gap: "8px",
            color: "#ddd", fontFamily: "monospace", fontSize: "13px",
        }),
    });

    // current path bar
    const pathBar = el("div", {
        style: css({
            background: "#111", padding: "6px 10px", borderRadius: "4px",
            wordBreak: "break-all", minHeight: "28px", color: "#9cf",
        }),
    });

    // directory list
    const list = el("div", {
        style: css({
            overflowY: "auto", flex: "1",
            minHeight: "240px", maxHeight: "380px",
            background: "#111", borderRadius: "4px", padding: "4px",
        }),
    });

    // button row
    const btnRow = el("div", {
        style: css({ display: "flex", gap: "8px", justifyContent: "flex-end" }),
    });
    const selectBtn = styledBtn("Select This Folder", "#2a7a2a");
    const cancelBtn = styledBtn("Cancel", "#444");
    btnRow.append(cancelBtn, selectBtn);

    dialog.append(pathBar, list, btnRow);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    // --- state ---
    let currentPath = "";

    async function navigate(path) {
        setList('<div style="padding:8px;color:#888">Loading…</div>');
        try {
            const data  = await fetchDir(path ?? "");
            currentPath = data.path ?? "";
            pathBar.textContent = currentPath || "(select a drive)";
            list.innerHTML = "";

            if (data.parent !== null && data.parent !== undefined) {
                list.appendChild(makeEntry("⬆  ..", () => navigate(data.parent)));
            }
            for (const dir of data.dirs ?? []) {
                list.appendChild(makeEntry("📁  " + dir.name, () => navigate(dir.path)));
            }
            if (!(data.dirs?.length)) {
                setList('<div style="padding:8px;color:#888">No subdirectories.</div>');
            }
        } catch (e) {
            setList(`<div style="padding:8px;color:#f66">Error: ${e.message}</div>`);
        }
    }

    function setList(html) { list.innerHTML = html; }

    function makeEntry(label, onClick) {
        const entry = el("div", {
            style: css({
                padding: "5px 10px", cursor: "pointer", borderRadius: "3px",
                whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
            }),
            textContent: label,
        });
        entry.addEventListener("mouseenter", () => entry.style.background = "#2a2a3e");
        entry.addEventListener("mouseleave", () => entry.style.background = "");
        entry.addEventListener("click", onClick);
        return entry;
    }

    // --- close helpers ---
    function close() {
        overlay.remove();
        document.removeEventListener("keydown", onKey);
    }
    function onKey(e) { if (e.key === "Escape") close(); }
    document.addEventListener("keydown", onKey);

    selectBtn.addEventListener("click", () => {
        if (currentPath) onSelect(currentPath);
        close();
    });
    cancelBtn.addEventListener("click", close);
    overlay.addEventListener("click", e => { if (e.target === overlay) close(); });

    navigate(startPath || null);
}

// ---------------------------------------------------------------------------
// Tiny DOM helpers
// ---------------------------------------------------------------------------

function el(tag, props = {}) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
        if (k === "style") node.style.cssText = v;
        else node[k] = v;
    }
    return node;
}

function css(obj) {
    return Object.entries(obj).map(([k, v]) =>
        k.replace(/[A-Z]/g, c => "-" + c.toLowerCase()) + ":" + v
    ).join(";");
}

function styledBtn(label, bg) {
    return el("button", {
        textContent: label,
        style: css({
            padding: "6px 14px", background: bg, border: "none",
            borderRadius: "4px", color: "#fff", cursor: "pointer",
        }),
    });
}
