(function () {
    let panel = null;
    let activeInput = null;
    let activeItems = [];
    let activeIndex = -1;

    function ensurePanel() {
        if (panel) return panel;

        panel = document.createElement("div");
        panel.className = "liquid-suggest-panel";
        document.body.appendChild(panel);

        return panel;
    }

    function normalizeText(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    function getSourceOptions(sourceSelector) {
        const source = document.querySelector(sourceSelector);
        if (!source) return [];

        return Array.from(source.querySelectorAll("option"))
            .filter(option => option.value)
            .map(option => ({
                value: option.value,
                label: option.textContent.trim(),
                code: option.dataset.code || "",
                name: option.dataset.name || option.textContent.trim(),
                unit: option.dataset.unit || "",
                grade: option.dataset.grade || "",
                group: option.dataset.group || "",
                stock: option.dataset.stock || "",
                supplier: option.dataset.supplier || "",
                supplierCode: option.dataset.supplierCode || "",
                rawOption: option
            }));
    }

    function positionPanel(input) {
        const box = input.getBoundingClientRect();
        const p = ensurePanel();

        const width = Math.max(box.width, 420);
        let left = box.left;
        let top = box.bottom + 8;

        if (left + width > window.innerWidth - 16) {
            left = window.innerWidth - width - 16;
        }

        if (left < 16) {
            left = 16;
        }

        p.style.width = `${width}px`;
        p.style.left = `${left}px`;
        p.style.top = `${top}px`;
    }

    function closePanel() {
        if (!panel) return;

        panel.classList.remove("is-open");
        panel.innerHTML = "";
        activeInput = null;
        activeItems = [];
        activeIndex = -1;
    }

    function chooseItem(item) {
        if (!activeInput) return;

        const hiddenTarget = activeInput.dataset.liquidTarget;
        const displayMode = activeInput.dataset.liquidDisplay || "name";

        if (displayMode === "code-name") {
            activeInput.value = `${item.code} - ${item.name}`;
        } else {
            activeInput.value = item.name;
        }

        activeInput.dataset.selectedValue = item.value;
        activeInput.dataset.code = item.code;
        activeInput.dataset.name = item.name;
        activeInput.dataset.unit = item.unit;
        activeInput.dataset.grade = item.grade;
        activeInput.dataset.group = item.group;
        activeInput.dataset.stock = item.stock;
        activeInput.dataset.supplier = item.supplier;
        activeInput.dataset.supplierCode = item.supplierCode;

        if (hiddenTarget) {
            const hidden = document.querySelector(hiddenTarget);
            if (hidden) hidden.value = item.value;
        }

        activeInput.dispatchEvent(new CustomEvent("liquid-suggest:selected", {
            bubbles: true,
            detail: item
        }));

        closePanel();
    }

    function renderPanel(input) {
        const sourceSelector = input.dataset.liquidSource;
        const query = normalizeText(input.value);
        const allItems = getSourceOptions(sourceSelector);

        activeItems = allItems.filter(item => {
            const haystack = normalizeText(`${item.code} ${item.name} ${item.label} ${item.supplier}`);
            return !query || haystack.includes(query);
        }).slice(0, 30);

        const p = ensurePanel();
        p.innerHTML = "";

        const state = document.createElement("div");
        state.className = "liquid-suggest-search-state";
        state.textContent = activeItems.length
            ? `Gợi ý sản phẩm (${activeItems.length})`
            : "Không tìm thấy sản phẩm";
        p.appendChild(state);

        if (!activeItems.length) {
            const empty = document.createElement("div");
            empty.className = "liquid-suggest-empty";
            empty.textContent = "Không có sản phẩm phù hợp. Hãy kiểm tra nhóm hàng hoặc từ khóa.";
            p.appendChild(empty);
        }

        activeItems.forEach((item, index) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "liquid-suggest-item";
            btn.dataset.index = String(index);

            btn.innerHTML = `
                <div class="liquid-suggest-icon">
                    ${item.group || "SP"}
                </div>
                <div class="liquid-suggest-main">
                    <div class="liquid-suggest-title">${item.name}</div>
                    <div class="liquid-suggest-sub">
                        <span class="liquid-suggest-code">${item.code || "-"}</span>
                        ${item.unit ? `<span>${item.unit}</span>` : ""}
                        ${item.supplier ? `<span>${item.supplier}</span>` : ""}
                    </div>
                </div>
                <div class="liquid-suggest-pill">
                    ${item.stock !== "" ? `Tồn ${item.stock}` : "Chọn"}
                </div>
            `;

            btn.addEventListener("mousedown", function (event) {
                event.preventDefault();
                chooseItem(item);
            });

            p.appendChild(btn);
        });

        activeIndex = -1;
        positionPanel(input);
        p.classList.add("is-open");
    }

    function setActiveIndex(nextIndex) {
        if (!panel || !activeItems.length) return;

        const items = panel.querySelectorAll(".liquid-suggest-item");
        items.forEach(item => item.classList.remove("is-active"));

        activeIndex = nextIndex;

        if (activeIndex < 0) activeIndex = activeItems.length - 1;
        if (activeIndex >= activeItems.length) activeIndex = 0;

        const activeEl = items[activeIndex];
        if (activeEl) {
            activeEl.classList.add("is-active");
            activeEl.scrollIntoView({ block: "nearest" });
        }
    }

    function bindInput(input) {
        if (input.dataset.liquidSuggestBound === "1") return;
        input.dataset.liquidSuggestBound = "1";

        input.setAttribute("autocomplete", "off");

        input.addEventListener("focus", function () {
            activeInput = input;
            renderPanel(input);
        });

        input.addEventListener("input", function () {
            activeInput = input;
            renderPanel(input);
        });

        input.addEventListener("keydown", function (event) {
            if (!panel || !panel.classList.contains("is-open")) return;

            if (event.key === "ArrowDown") {
                event.preventDefault();
                setActiveIndex(activeIndex + 1);
            }

            if (event.key === "ArrowUp") {
                event.preventDefault();
                setActiveIndex(activeIndex - 1);
            }

            if (event.key === "Enter") {
                if (activeIndex >= 0 && activeItems[activeIndex]) {
                    event.preventDefault();
                    chooseItem(activeItems[activeIndex]);
                }
            }

            if (event.key === "Escape") {
                closePanel();
            }
        });
    }

    function bindClearButtons() {
        document.querySelectorAll("[data-liquid-clear]").forEach(btn => {
            if (btn.dataset.liquidClearBound === "1") return;
            btn.dataset.liquidClearBound = "1";

            btn.addEventListener("click", function () {
                const selector = btn.dataset.liquidClear;
                const input = document.querySelector(selector);

                if (input) {
                    input.value = "";
                    input.dataset.selectedValue = "";
                    input.focus();
                    input.dispatchEvent(new Event("input", { bubbles: true }));
                }
            });
        });
    }

    function initLiquidSuggest() {
        document.querySelectorAll("[data-liquid-suggest='product']").forEach(bindInput);
        bindClearButtons();
    }

    document.addEventListener("click", function (event) {
        if (!panel) return;

        const clickedInsidePanel = panel.contains(event.target);
        const clickedInput = event.target.closest("[data-liquid-suggest='product']");

        if (!clickedInsidePanel && !clickedInput) {
            closePanel();
        }
    });

    window.addEventListener("resize", function () {
        if (activeInput && panel && panel.classList.contains("is-open")) {
            positionPanel(activeInput);
        }
    });

    window.LiquidSuggest = {
        init: initLiquidSuggest,
        close: closePanel
    };

    document.addEventListener("DOMContentLoaded", initLiquidSuggest);
})();