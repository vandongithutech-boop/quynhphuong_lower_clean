document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("select").forEach(originalSelect => {
        if (originalSelect.dataset.customReady === "1") return;
        if (originalSelect.classList.contains("no-custom-select")) return;

        originalSelect.dataset.customReady = "1";
        originalSelect.classList.add("custom-select-hidden");

        const wrapper = document.createElement("div");
        wrapper.className = "custom-select-wrapper";

        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "custom-select-trigger";

        const value = document.createElement("span");
        value.className = "custom-select-value";
        value.textContent = originalSelect.options[originalSelect.selectedIndex]?.text || "Chọn";

        const icon = document.createElement("i");
        icon.className = "bi bi-chevron-down custom-select-icon";

        trigger.appendChild(value);
        trigger.appendChild(icon);

        const menu = document.createElement("div");
        menu.className = "custom-select-menu";

        Array.from(originalSelect.options).forEach(option => {
            const item = document.createElement("button");
            item.type = "button";
            item.className = "custom-select-option";
            item.textContent = option.text;
            item.dataset.value = option.value;

            if (option.selected) item.classList.add("active");
            if (option.disabled) item.disabled = true;

            item.addEventListener("click", function () {
                originalSelect.value = option.value;
                value.textContent = option.text;

                menu.querySelectorAll(".custom-select-option").forEach(btn => {
                    btn.classList.remove("active");
                });

                item.classList.add("active");
                wrapper.classList.remove("open");

                originalSelect.dispatchEvent(new Event("change", { bubbles: true }));
            });

            menu.appendChild(item);
        });

        trigger.addEventListener("click", function () {
            document.querySelectorAll(".custom-select-wrapper.open").forEach(opened => {
                if (opened !== wrapper) opened.classList.remove("open");
            });

            wrapper.classList.toggle("open");
        });

        originalSelect.parentNode.insertBefore(wrapper, originalSelect);
        wrapper.appendChild(originalSelect);
        wrapper.appendChild(trigger);
        wrapper.appendChild(menu);
    });

    document.addEventListener("click", function (e) {
        if (!e.target.closest(".custom-select-wrapper")) {
            document.querySelectorAll(".custom-select-wrapper.open").forEach(wrapper => {
                wrapper.classList.remove("open");
            });
        }
    });
});