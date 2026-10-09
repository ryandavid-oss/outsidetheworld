(function () {
    "use strict";

    var SVG_NS = "http://www.w3.org/2000/svg";
    var DPI = 300;
    var COLORS = { white: "#ffffff", ink: "#1a1c20" };
    var SHAPES = { rounded: "Rounded rectangle", rectangle: "Rectangle", circle: "Circle" };
    var state = { artworkId: "", shape: "circle", width: 3, height: 3, scale: 100, border: 0.12, color: "white", quantity: 1 };
    var artwork = null;
    var artworkRevision = 0;
    var renderRevision = 0;
    var loading = false;
    var exporting = false;
    var automaticHeight = false;
    var artworkCache = new Map();
    var preview = document.getElementById("stickerPreview");
    var previewContext = preview.getContext("2d");
    var grid = document.getElementById("artworkGrid");
    var widthInput = document.getElementById("stickerWidth");
    var heightInput = document.getElementById("stickerHeight");
    var quantityInput = document.getElementById("stickerQuantity");
    var scaleInput = document.getElementById("artworkScale");
    var borderInput = document.getElementById("borderSpacing");
    var renderState = document.getElementById("renderState");
    var message = document.getElementById("systemMessage");
    var exportButtons = Array.from(document.querySelectorAll(".export-actions button"));

    function tell(text, error) {
        message.textContent = text;
        message.dataset.level = error ? "error" : "ok";
    }

    function validInputs() {
        return [widthInput, quantityInput].concat(state.shape === "circle" ? [] : [heightInput])
            .every(function (input) { return input.value !== "" && input.validity.valid; });
    }

    function sync() {
        document.querySelectorAll("[data-artwork]").forEach(function (button) {
            button.setAttribute("aria-pressed", String(button.dataset.artwork === state.artworkId));
        });
        ["shape", "color"].forEach(function (key) {
            document.querySelectorAll("[data-" + key + "]").forEach(function (button) {
                button.setAttribute("aria-pressed", String(button.dataset[key] === state[key]));
            });
        });
        document.getElementById("widthLabel").textContent = state.shape === "circle" ? "Diameter (inches)" : "Width (inches)";
        heightInput.disabled = state.shape === "circle";
        if (document.activeElement !== widthInput) widthInput.value = state.width;
        if (document.activeElement !== heightInput) heightInput.value = state.shape === "circle" ? state.width : state.height;
        var maxBorder = Math.min(0.5, (Math.min(state.width, state.shape === "circle" ? state.width : state.height) / 2) - 0.03);
        borderInput.max = maxBorder.toFixed(2);
        state.border = Math.min(state.border, Number(borderInput.max));
        borderInput.value = state.border;
        scaleInput.value = state.scale;
        document.getElementById("borderValue").textContent = state.border.toFixed(2) + " in";
        document.getElementById("scaleValue").textContent = state.scale + "%";
        document.getElementById("designReadout").textContent = artwork ? artwork.label : "—";
        document.getElementById("sizeReadout").textContent = state.shape === "circle"
            ? state.width + " in diameter" : state.width + " × " + state.height + " in";
        exportButtons.forEach(function (button) { button.disabled = !artwork || loading || exporting || !validInputs(); });
    }

    function prepareSvg(source, label, id) {
        if (source.length > 2000000 || /<!ENTITY/i.test(source)) throw new Error("Choose an SVG smaller than 2 MB with outlined artwork.");
        var doc = new DOMParser().parseFromString(source, "image/svg+xml");
        var root = doc.documentElement;
        if (doc.querySelector("parsererror") || root.localName !== "svg" || root.namespaceURI !== SVG_NS) {
            throw new Error("That file could not be read as SVG artwork.");
        }
        var viewBox = (root.getAttribute("viewBox") || "").trim().split(/[\s,]+/).map(Number);
        if (viewBox.length !== 4 || !viewBox.every(Number.isFinite) || viewBox[2] <= 0 || viewBox[3] <= 0 || viewBox[2] > 100000 || viewBox[3] > 100000) {
            throw new Error("This SVG needs a valid viewBox. Export it with an artboard and try again.");
        }
        var elements = [root].concat(Array.from(root.querySelectorAll("*")));
        if (elements.length > 10000) throw new Error("That SVG is too complex. Try a simpler vector export.");
        var tags = new Set("svg g defs path rect circle ellipse line polyline polygon use clipPath mask linearGradient radialGradient stop pattern filter feBlend feColorMatrix feComponentTransfer feComposite feConvolveMatrix feDiffuseLighting feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMerge feMergeNode feMorphology feOffset fePointLight feSpecularLighting feSpotLight feTile feTurbulence title desc".split(" "));
        var properties = new Set("fill fill-opacity fill-rule stroke stroke-width stroke-opacity stroke-linecap stroke-linejoin stroke-miterlimit stroke-dasharray stroke-dashoffset clip-rule clip-path mask filter opacity color stop-color stop-opacity flood-color flood-opacity lighting-color paint-order vector-effect display visibility isolation mix-blend-mode".split(" "));
        function localReferences(value) {
            if (/@|expression\s*\(|var\s*\(/i.test(value)) return false;
            var stripped = value.replace(/url\(\s*["']?#[\w.-]+["']?\s*\)/gi, "");
            return !/url\s*\(/i.test(stripped);
        }
        elements.forEach(function (element) {
            if (element.namespaceURI !== SVG_NS || !tags.has(element.localName)) {
                throw new Error("Use vector paths with inline styles. Outline text and remove scripts or embedded media before exporting.");
            }
            Array.from(element.attributes).forEach(function (attribute) {
                if (/^on/i.test(attribute.localName) || (attribute.localName === "href" && !/^#[\w.-]+$/.test(attribute.value)) || !localReferences(attribute.value)) {
                    throw new Error("This SVG includes outside resources. Export self-contained vector artwork and try again.");
                }
                if (attribute.name === "style") {
                    var cleanStyle = [];
                    Array.from(element.style).forEach(function (property) {
                        if (!properties.has(property)) throw new Error("Use outlined vector artwork with inline SVG styles.");
                        cleanStyle.push(property + ":" + element.style.getPropertyValue(property));
                    });
                    element.setAttribute("style", cleanStyle.join(";"));
                }
            });
        });
        // Keep imported IDs separate from the sticker's own clipping path.
        var ids = new Map();
        elements.forEach(function (element) {
            if (element.id) { ids.set(element.id, "design-" + element.id); element.id = "design-" + element.id; }
        });
        elements.forEach(function (element) {
            Array.from(element.attributes).forEach(function (attribute) {
                var value = attribute.value.replace(/url\(\s*["']?#([\w.-]+)["']?\s*\)/gi, function (match, target) {
                    return ids.has(target) ? "url(#" + ids.get(target) + ")" : match;
                });
                if (attribute.localName === "href" && ids.has(value.slice(1))) value = "#" + ids.get(value.slice(1));
                attribute.value = value;
            });
        });
        root.setAttribute("viewBox", viewBox.join(" "));
        root.setAttribute("overflow", "hidden");
        return { root: root, original: source, label: label, id: id, viewBox: viewBox, width: viewBox[2], height: viewBox[3] };
    }

    async function measureArtwork(design) {
        // Measure visible artwork, including strokes, without flattening the vector export.
        var sampleScale = 2048 / Math.max(design.width, design.height);
        var canvas = document.createElement("canvas");
        canvas.width = Math.max(1, Math.round(design.width * sampleScale));
        canvas.height = Math.max(1, Math.round(design.height * sampleScale));
        var sample = design.root.cloneNode(true);
        sample.setAttribute("width", canvas.width);
        sample.setAttribute("height", canvas.height);
        var image = await svgImage(new XMLSerializer().serializeToString(sample));
        var context = canvas.getContext("2d", { willReadFrequently: true });
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        var pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
        var left = canvas.width, right = -1, top = canvas.height, bottom = -1;
        var edges = [];
        for (var y = 0; y < canvas.height; y += 1) {
            var rowLeft = canvas.width, rowRight = -1;
            for (var x = 0; x < canvas.width; x += 1) {
                if (pixels[(y * canvas.width + x) * 4 + 3] === 0) continue;
                rowLeft = Math.min(rowLeft, x);
                rowRight = x;
            }
            if (rowRight < 0) continue;
            left = Math.min(left, rowLeft); right = Math.max(right, rowRight);
            top = Math.min(top, y); bottom = y;
            edges.push([rowLeft, y], [rowRight + 1, y + 1]);
        }
        if (right < 0) throw new Error("That SVG has no visible artwork. Choose another design.");
        // One sampled pixel protects antialiased edges when tightening the viewBox.
        left = Math.max(0, left - 1); top = Math.max(0, top - 1);
        right = Math.min(canvas.width, right + 2); bottom = Math.min(canvas.height, bottom + 2);
        var unitsX = design.width / canvas.width, unitsY = design.height / canvas.height;
        var centerX = (left + right) / 2, centerY = (top + bottom) / 2;
        var radius = 0;
        edges.forEach(function (point) {
            radius = Math.max(radius, Math.hypot((point[0] - centerX) * unitsX, (point[1] - centerY) * unitsY));
        });
        design.radius = radius + Math.hypot(unitsX, unitsY);
        design.width = (right - left) * unitsX;
        design.height = (bottom - top) * unitsY;
        design.root.setAttribute("viewBox", [design.viewBox[0] + left * unitsX, design.viewBox[1] + top * unitsY, design.width, design.height].join(" "));
        return design;
    }

    function fitHeight(design) {
        state.height = Math.min(8, Math.max(0.75, Math.ceil(((state.width - state.border * 2) * design.height / design.width + state.border * 2) * 100) / 100));
    }

    function fitArtworkDefaults(design) {
        state.shape = design.width / design.height > 2.5 ? "rounded" : "circle";
        state.scale = 100;
        state.color = "white";
        automaticHeight = state.shape === "rounded";
        if (automaticHeight) fitHeight(design);
        else state.height = state.width;
    }

    function svgElement(name, attributes) {
        var element = document.createElementNS(SVG_NS, name);
        Object.keys(attributes || {}).forEach(function (key) { element.setAttribute(key, attributes[key]); });
        return element;
    }

    function composeSvg(settings, design) {
        var width = Math.round(settings.width * DPI);
        var height = settings.shape === "circle" ? width : Math.round(settings.height * DPI);
        var root = svgElement("svg", { xmlns: SVG_NS, width: settings.width + "in", height: (settings.shape === "circle" ? settings.width : settings.height) + "in", viewBox: "0 0 " + width + " " + height });
        var title = svgElement("title");
        title.textContent = design.label + " sticker";
        root.appendChild(title);
        var shape = settings.shape === "circle"
            ? svgElement("circle", { cx: width / 2, cy: height / 2, r: width / 2 })
            : svgElement("rect", { width: width, height: height, rx: settings.shape === "rounded" ? Math.min(width, height) * 0.12 : 0 });
        var definitions = svgElement("defs");
        var clip = svgElement("clipPath", { id: "otw-sticker-clip" });
        clip.appendChild(shape.cloneNode(true));
        definitions.appendChild(clip);
        root.appendChild(definitions);
        shape.setAttribute("fill", COLORS[settings.color]);
        root.appendChild(shape);
        var padding = settings.border * DPI;
        var availableWidth = width - padding * 2;
        var availableHeight = height - padding * 2;
        var fit = settings.shape === "circle"
            ? (width / 2 - padding) / design.radius
            : Math.min(availableWidth / design.width, availableHeight / design.height);
        if (settings.shape === "rounded") {
            var radius = Math.min(width, height) * 0.12;
            var insetRadius = Math.max(0, radius - padding);
            var low = 0, high = fit;
            for (var iteration = 0; iteration < 24; iteration += 1) {
                var candidate = (low + high) / 2;
                var dx = Math.max(0, design.width * candidate / 2 - (width / 2 - radius));
                var dy = Math.max(0, design.height * candidate / 2 - (height / 2 - radius));
                if (dx * dx + dy * dy <= insetRadius * insetRadius) low = candidate;
                else high = candidate;
            }
            fit = low;
        }
        fit *= settings.scale / 100;
        var artWidth = design.width * fit;
        var artHeight = design.height * fit;
        var content = svgElement("g", { "clip-path": "url(#otw-sticker-clip)" });
        var art = design.root.cloneNode(true);
        art.setAttribute("x", (width - artWidth) / 2);
        art.setAttribute("y", (height - artHeight) / 2);
        art.setAttribute("width", artWidth);
        art.setAttribute("height", artHeight);
        content.appendChild(art);
        root.appendChild(content);
        return { source: new XMLSerializer().serializeToString(root), width: width, height: height };
    }

    function svgImage(source) {
        return new Promise(function (resolve, reject) {
            var url = URL.createObjectURL(new Blob([source], { type: "image/svg+xml" }));
            var image = new Image();
            var timeout = window.setTimeout(function () { URL.revokeObjectURL(url); reject(new Error("The SVG took too long to render.")); }, 15000);
            image.onload = function () { window.clearTimeout(timeout); URL.revokeObjectURL(url); resolve(image); };
            image.onerror = function () { window.clearTimeout(timeout); URL.revokeObjectURL(url); reject(new Error("The SVG could not be rendered.")); };
            image.src = url;
        });
    }

    async function render() {
        var revision = ++renderRevision;
        if (!artwork) return;
        var design = artwork;
        var settings = Object.assign({}, state);
        renderState.textContent = "Rendering…";
        try {
            var composition = composeSvg(settings, design);
            var image = await svgImage(composition.source);
            if (revision !== renderRevision) return;
            previewContext.clearRect(0, 0, preview.width, preview.height);
            var fit = 960 / Math.max(composition.width, composition.height);
            var width = composition.width * fit, height = composition.height * fit;
            previewContext.drawImage(image, (1200 - width) / 2, (1200 - height) / 2, width, height);
            preview.setAttribute("aria-label", design.label + ", " + SHAPES[settings.shape].toLowerCase() + " sticker, " + settings.width + " by " + (settings.shape === "circle" ? settings.width : settings.height) + " inches");
            renderState.textContent = "Ready";
        } catch (error) {
            if (revision !== renderRevision) return;
            renderState.textContent = "Try another SVG";
            tell(error.message, true);
        }
    }

    async function selectArtwork(entry, file) {
        var revision = ++artworkRevision;
        renderRevision += 1;
        loading = true;
        renderState.textContent = "Loading artwork";
        sync();
        try {
            var design;
            if (file) {
                if (file.size > 2000000) throw new Error("Choose an SVG smaller than 2 MB.");
                design = await measureArtwork(prepareSvg(await file.text(), file.name.replace(/\.svg$/i, ""), "custom"));
            } else {
                if (!artworkCache.has(entry.id)) {
                    artworkCache.set(entry.id, fetch(entry.path).then(async function (response) {
                        if (!response.ok) throw new Error("That artwork could not be loaded. Try another design.");
                        return measureArtwork(prepareSvg(await response.text(), entry.label, entry.id));
                    }).catch(function (error) { artworkCache.delete(entry.id); throw error; }));
                }
                design = await artworkCache.get(entry.id);
            }
            if (revision !== artworkRevision) return;
            artwork = design;
            state.artworkId = design.id;
            fitArtworkDefaults(design);
            tell(design.label + " selected.");
        } catch (error) {
            if (revision !== artworkRevision) return;
            tell(error.message, true);
        } finally {
            if (revision === artworkRevision) { loading = false; sync(); render(); }
        }
    }

    function crc32(bytes) {
        var crc = 0xffffffff;
        for (var index = 0; index < bytes.length; index += 1) {
            crc ^= bytes[index];
            for (var bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
        }
        return (crc ^ 0xffffffff) >>> 0;
    }

    async function pngWithDensity(canvas) {
        var blob = await new Promise(function (resolve) { canvas.toBlob(resolve, "image/png"); });
        if (!blob) throw new Error("The PNG could not be created.");
        var bytes = new Uint8Array(await blob.arrayBuffer());
        var view = new DataView(bytes.buffer);
        var density = new Uint8Array(21);
        var densityView = new DataView(density.buffer);
        densityView.setUint32(0, 9);
        density.set([112, 72, 89, 115], 4); // pHYs: physical pixels per metre.
        densityView.setUint32(8, Math.round(DPI / 0.0254));
        densityView.setUint32(12, Math.round(DPI / 0.0254));
        density[16] = 1;
        densityView.setUint32(17, crc32(density.subarray(4, 17)));
        var parts = [bytes.subarray(0, 8)];
        for (var offset = 8; offset < bytes.length;) {
            var end = offset + 12 + view.getUint32(offset);
            var type = String.fromCharCode.apply(null, bytes.subarray(offset + 4, offset + 8));
            if (type !== "pHYs") parts.push(bytes.subarray(offset, end));
            if (type === "IHDR") parts.push(density);
            offset = end;
        }
        return new Blob(parts, { type: "image/png" });
    }

    async function printPng(composition) {
        var image = await svgImage(composition.source);
        var canvas = document.createElement("canvas");
        canvas.width = composition.width;
        canvas.height = composition.height;
        canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height);
        return pngWithDensity(canvas);
    }

    async function storedZip(files) {
        var locals = [], central = [], offset = 0;
        var encoder = new TextEncoder();
        for (var file of files) {
            var name = encoder.encode(file.name);
            var data = typeof file.data === "string" ? encoder.encode(file.data) : new Uint8Array(await file.data.arrayBuffer());
            var checksum = crc32(data);
            var local = new Uint8Array(30), localView = new DataView(local.buffer);
            localView.setUint32(0, 0x04034b50, true);
            localView.setUint16(4, 20, true);
            localView.setUint16(6, 0x800, true);
            localView.setUint16(12, 33, true); // January 1, 1980: a valid deterministic ZIP date.
            localView.setUint32(14, checksum, true);
            localView.setUint32(18, data.length, true);
            localView.setUint32(22, data.length, true);
            localView.setUint16(26, name.length, true);
            locals.push(local, name, data);
            var entry = new Uint8Array(46), entryView = new DataView(entry.buffer);
            entryView.setUint32(0, 0x02014b50, true);
            entryView.setUint16(4, 20, true);
            entryView.setUint16(6, 20, true);
            entryView.setUint16(8, 0x800, true);
            entryView.setUint16(14, 33, true);
            entryView.setUint32(16, checksum, true);
            entryView.setUint32(20, data.length, true);
            entryView.setUint32(24, data.length, true);
            entryView.setUint16(28, name.length, true);
            entryView.setUint32(42, offset, true);
            central.push(entry, name);
            offset += local.length + name.length + data.length;
        }
        var end = new Uint8Array(22), endView = new DataView(end.buffer);
        endView.setUint32(0, 0x06054b50, true);
        endView.setUint16(8, files.length, true);
        endView.setUint16(10, files.length, true);
        endView.setUint32(12, central.reduce(function (size, item) { return size + item.length; }, 0), true);
        endView.setUint32(16, offset, true);
        return new Blob(locals.concat(central, [end]), { type: "application/zip" });
    }

    function download(blob, filename) {
        var url = URL.createObjectURL(blob);
        var link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
    }

    function packagePath(folder, name, extension) {
        return folder + "/" + name + "." + extension;
    }

    async function exportDesign(kind) {
        if (!artwork || loading || exporting || !validInputs()) return;
        exporting = true;
        var settings = Object.assign({}, state), design = artwork;
        sync();
        tell("Preparing " + design.label + "…");
        try {
            var composition = composeSvg(settings, design);
            var stem = "sticker-" + design.id + "-" + settings.shape + "-" + settings.width + "x" + (settings.shape === "circle" ? settings.width : settings.height) + "in";
            var svg = new Blob([composition.source], { type: "image/svg+xml" });
            if (kind === "svg") download(svg, stem + ".svg");
            else if (kind === "png") download(await printPng(composition), stem + ".png");
            else {
                var instructions = [
                    "STICKERS / OUTSIDE THE WORLD", "",
                    "Design: " + design.label,
                    "Quantity: " + settings.quantity,
                    "Size: " + settings.width + " x " + (settings.shape === "circle" ? settings.width : settings.height) + " inches",
                    "Shape: " + SHAPES[settings.shape], "",
                    "Print artwork.svg at the stated size. Cut to the outside edge of the sticker shape.",
                    "artwork.png is the same design at 300 DPI.",
                    "original.svg is the source artwork for reference."
                ].join("\n");
                var zip = await storedZip([
                    { name: packagePath(stem, "artwork", "svg"), data: svg },
                    { name: packagePath(stem, "artwork", "png"), data: await printPng(composition) },
                    { name: packagePath(stem, "original", "svg"), data: design.original },
                    { name: stem + "/print-notes.txt", data: instructions }
                ]);
                download(zip, stem + ".zip");
            }
            tell("Exported " + design.label + ".");
        } catch (error) { tell(error.message || "The export could not be created. Please try again.", true); }
        finally { exporting = false; sync(); }
    }

    [widthInput, heightInput, quantityInput].forEach(function (input) {
        input.addEventListener("input", function () {
            if (!validInputs()) { tell("Enter dimensions from 0.75 to 8 inches and a whole-number quantity from 1 to 10,000.", true); sync(); return; }
            state.width = Number(widthInput.value);
            if (state.shape !== "circle") state.height = Number(heightInput.value);
            if (input === heightInput) automaticHeight = false;
            if (input === widthInput && automaticHeight && artwork) fitHeight(artwork);
            state.quantity = Number(quantityInput.value);
            tell("Size and quantity updated.");
            sync(); render();
        });
    });
    document.querySelectorAll("[data-shape], [data-color]").forEach(function (button) {
        button.addEventListener("click", function () {
            if (button.dataset.shape) {
                state.shape = button.dataset.shape;
                automaticHeight = state.shape !== "circle";
                if (automaticHeight && artwork) fitHeight(artwork);
            }
            if (button.dataset.color) state.color = button.dataset.color;
            sync(); render();
        });
    });
    [scaleInput, borderInput].forEach(function (input) {
        input.addEventListener("input", function () {
            state.scale = Number(scaleInput.value);
            state.border = Number(borderInput.value);
            if (input === borderInput && automaticHeight && artwork) fitHeight(artwork);
            sync(); render();
        });
    });
    document.getElementById("svgUpload").addEventListener("change", function (event) {
        var file = event.target.files[0];
        if (file) selectArtwork(null, file);
    });
    document.getElementById("exportSvg").addEventListener("click", function () { exportDesign("svg"); });
    document.getElementById("exportPng").addEventListener("click", function () { exportDesign("png"); });
    document.getElementById("exportPackage").addEventListener("click", function () { exportDesign("zip"); });

    async function init() {
        try {
            var response = await fetch("/data/products/stickers.json");
            if (!response.ok) throw new Error("The artwork collection could not be loaded. You can still choose your own SVG.");
            var entries = await response.json();
            var ids = new Set();
            if (!Array.isArray(entries)) throw new Error("The artwork collection could not be read. Choose your own SVG to continue.");
            entries.forEach(function (entry) {
                if (!entry || !/^[a-z0-9-]+$/.test(entry.id) || ids.has(entry.id) || typeof entry.label !== "string" || !/^\/Images\/Stickers\/[a-z0-9-]+\.svg$/.test(entry.path)) throw new Error("The artwork collection could not be read. Choose your own SVG to continue.");
                ids.add(entry.id);
                var button = document.createElement("button");
                button.type = "button";
                button.className = "button artwork-choice";
                button.dataset.artwork = entry.id;
                button.setAttribute("aria-pressed", "false");
                var image = document.createElement("img");
                image.src = entry.path;
                image.alt = "";
                if (entry.id.endsWith("dark")) image.className = "artwork-thumb--light";
                var label = document.createElement("span");
                label.textContent = entry.label;
                button.append(image, label);
                button.addEventListener("click", function () { selectArtwork(entry); });
                grid.appendChild(button);
            });
            // An upload made while the catalog loads takes precedence over the default.
            if (entries.length && artworkRevision === 0) await selectArtwork(entries[0]);
            else if (!entries.length && artworkRevision === 0) renderState.textContent = "Choose an SVG";
        } catch (error) { tell(error.message, true); if (!artwork) renderState.textContent = "Choose an SVG"; }
    }
    sync();
    init();
})();
