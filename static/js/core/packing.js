function getPackingTotalStems() {
    let total = 0;

    document.querySelectorAll('input[name^="packing_quantity_"]').forEach(input => {
        total += parseFloat(input.value || 0);
    });

    return total;
}

function getFirstProductInfo() {

    const firstRow = document.querySelector(".packing-row");

    if (!firstRow) {
        return {
            productCode: "",
            productName: ""
        };
    }

    const nameEl = firstRow.querySelector(".product-name");
    const text = nameEl ? nameEl.innerText.trim() : "";

    const parts = text.split("/");

    return {
        productCode: parts[0] ? parts[0].trim() : "",
        productName: parts[1] ? parts[1].trim() : text,
    };
}

function updateBoxSuggestion() {

    const checkedRule = document.querySelector('input[name="stem_rule_id"]:checked');

    const resultBox = document.getElementById("boxSuggestionResult");

    if (!checkedRule || !resultBox) return;

    const totalStems = getPackingTotalStems();

    const stemsPerBunch = parseFloat(
        checkedRule.dataset.stems || 0
    );

    const product = getFirstProductInfo();

    if (totalStems <= 0 || stemsPerBunch <= 0) {

        resultBox.style.display = "none";
        resultBox.innerHTML = "";

        return;
    }

    const totalBunches = Math.ceil(
        totalStems / stemsPerBunch
    );

    fetch(
        `${PACKING_SUGGEST_API}?product_code=${encodeURIComponent(product.productCode)}&product_name=${encodeURIComponent(product.productName)}&stems=${totalStems}`
    )
    .then(res => res.json())

    .then(data => {

        resultBox.style.display = "block";

        resultBox.innerHTML = `
            <div class="suggest-title">
                <i class="bi bi-stars"></i>
                Gợi ý loại thùng
            </div>

            <div class="suggest-grid">

                <div>
                    <small>Tổng cành</small>
                    <strong>${totalStems}</strong>
                </div>

                <div>
                    <small>Quy cách</small>
                    <strong>${stemsPerBunch}c/bó</strong>
                </div>

                <div>
                    <small>Số bó dự kiến</small>
                    <strong>${totalBunches}</strong>
                </div>

                <div>
                    <small>Chỉ số</small>
                    <strong>${data.total_index || 0}</strong>
                </div>

                <div>
                    <small>Thùng gợi ý</small>
                    <strong>${data.box_code || "Chọn thủ công"}</strong>
                </div>

                <div>
                    <small>Trạng thái</small>
                    <strong>${data.status || "-"}</strong>
                </div>

            </div>

            <div class="suggest-message">
                ${data.message || ""}
            </div>
        `;

        if (data.box_code) {

            const suggestedBox = document.querySelector(
                `input[name="box_type_id"][data-code="${data.box_code}"]`
            );

            if (suggestedBox) {
                suggestedBox.checked = true;
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll('input[name="stem_rule_id"]')

    .forEach(input => {
        input.addEventListener(
            "change",
            updateBoxSuggestion
        );
    });

    document.querySelectorAll('input[name^="packing_quantity_"]')

    .forEach(input => {
        input.addEventListener(
            "input",
            updateBoxSuggestion
        );
    });
});