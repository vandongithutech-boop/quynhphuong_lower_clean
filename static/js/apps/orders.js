
let rowIndex = 0;
let selectedProducts = [];
let editingProductIndex = null;
let currentQuantityRow = null;
let currentFlowerTypeRow = null;

document.getElementById("customerSearch").addEventListener("input", function () {
    const q = this.value;
    const box = document.getElementById("customerResults");

    if (q.length < 1) {
        box.style.display = "none";
        return;
    }

    fetch(`/orders/api/customers/?q=${q}`)
        .then(res => res.json())
        .then(data => {
            box.innerHTML = "";

            data.customers.forEach(c => {
                const div = document.createElement("div");
                div.className = "suggest-item";
                div.innerHTML = `
                    <strong>${c.name}</strong> - ${c.code}<br>
                    <small>
                        ${c.address || ""}
                        | ${c.area || ""}
                        | ${c.phone || ""}
                        | ${c.transport || ""}
                    </small>
                `;

                div.onclick = function () {
                    document.getElementById("customerSearch").value = c.name;
                    document.getElementById("customerCode").value = c.code;
                    document.getElementById("customerName").value = c.name;
                    document.getElementById("customerAddress").value = c.address;
                    document.getElementById("customerArea").value = c.area;
                    document.getElementById("customerPhone").value = c.phone;
                    document.getElementById("needProcessingQty").value = data.can_process_qty || 0;
                    document.getElementById("rawAvailableQty").value = data.raw_available || 0;
                    document.getElementById("needProcessingQty").value = 0;
                    document.getElementById("rawAvailableQty").value = 0;
                    document.getElementById("previewCustomerName").innerText = c.name;
                    document.getElementById("previewCustomerInfo").innerText =
                    `${c.code} | ${c.address || ""} | ${c.area || ""} | ${c.phone || ""} | ${c.transport || ""}`;

                    box.style.display = "none";
                };

                box.appendChild(div);
            });

            box.style.display = "block";
        });
});

function addOrderItemRow() {
    rowIndex++;

    document.getElementById("orderItemRows").innerHTML = "";

    const html = `
        <div class="order-item-row">
            <div class="row g-3 align-items-end">
                <div class="col-md-2">
                    <label class="form-label">Phân loại</label>
                    <button type="button"
                            class="btn flower-type-btn w-100"
                            onclick="openFlowerTypePopup(this)">
                        Chọn
                    </button>
                    <input type="hidden" class="flower-type-value">
                </div>

                <div class="col-md-3">
                    <label class="form-label">Tên Hoa/Lá phụ</label>
                    <div class="flower-search-wrap">
                        <input type="text"
                            class="form-control flower-search-input"
                            placeholder="Nhập tên hoặc mã sản phẩm..."
                            oninput="searchFlowerSuggest(this)"
                            autocomplete="off">

                        <div class="flower-suggest-box"></div>
                    </div>
                    <input type="hidden" name="lot_id[]">
                    <input type="hidden" name="lot_code[]">
                    <input type="hidden" name="product_code[]">
                    <input type="hidden" name="product_name[]">
                    <input type="hidden" name="flower_type[]">
                    <input type="hidden" name="group_name[]">
                    <input type="hidden" name="unit[]">
                    <input type="hidden" name="supplier_name[]">
                    <input type="hidden" name="specification[]" value="">
                </div>

                <div class="col-md-3">
                    <label class="form-label quantity-label">Số lượng</label>
                    <button type="button"
                            class="btn quantity-btn w-100"
                            onclick="openQuantityBox(this)">
                        Chọn số lượng
                    </button>

                    <input type="hidden" class="standard-input" name="standard_quantity[]" value="0">
                    <input type="hidden" class="sale-input" name="sale_quantity[]" value="0">
                </div>

                <div class="col-md-2">
                    <label class="form-label">DVT</label>
                    <input type="text" class="form-control unit-display" readonly>
                </div>

                <div class="col-md-2">
                    <label class="form-label">Tone/Nhóm</label>
                    <input type="text" class="form-control group-display" readonly>
                </div>
            </div>
        </div>
    `;
    document.getElementById("orderItemRows").insertAdjacentHTML("beforeend", html);
}

function getCurrentProductData() {
    const row = document.querySelector("#orderItemRows .order-item-row");

    if (!row) return null;

    return {
        lot_id: row.querySelector('input[name="lot_id[]"]').value,
        lot_code: row.querySelector('input[name="lot_code[]"]').value,

        product_code: row.querySelector('input[name="product_code[]"]').value,
        product_name: row.querySelector('input[name="product_name[]"]').value,
        flower_type: row.querySelector('input[name="flower_type[]"]').value,
        group_name: row.querySelector('input[name="group_name[]"]').value,
        unit: row.querySelector('input[name="unit[]"]').value,
        supplier_name: row.querySelector('input[name="supplier_name[]"]').value,
        standard_quantity: row.querySelector(".standard-input").value || 0,
        sale_quantity: row.querySelector(".sale-input").value || 0,
        specification: row.querySelector('input[name="specification[]"]').value || "",
        display_type: row.querySelector(".flower-type-btn").innerText || "",
        quantity_label: row.querySelector(".quantity-label").innerText || "Số lượng",
        quantity_text: row.querySelector(".quantity-btn").innerText || "Chọn số lượng",
        raw_warning_text: document.getElementById("rawStockWarning")?.innerText || "",
        need_processing_qty: document.getElementById("needProcessingQty")?.value || 0,
        raw_available_qty: document.getElementById("rawAvailableQty")?.value || 0,
    };
}


function saveCurrentProduct() {
    const product = getCurrentProductData();

    if (!product || !product.product_name) {
        alert("Vui lòng chọn Tên Hoa/Lá phụ.");
        return;
    }

    const standardQty = parseFloat(product.standard_quantity || 0);
    const saleQty = parseFloat(product.sale_quantity || 0);

    if (standardQty <= 0 && saleQty <= 0) {
        alert("Vui lòng nhập số lượng sản phẩm.");
        return;
    }

    if (editingProductIndex !== null) {
        selectedProducts[editingProductIndex] = product;
        editingProductIndex = null;
    } else {
        selectedProducts.push(product);
    }

    renderSelectedProducts();
    renderHiddenProductInputs();

    document.getElementById("orderItemRows").innerHTML = "";
    addOrderItemRow();
}

function resetProductInputForm() {
    document.getElementById("orderItemRows").innerHTML = "";
    addOrderItemRow();
}

function renderSelectedProducts() {
    const list = document.getElementById("selectedProductList");
    const count = document.getElementById("selectedProductCount");

    count.innerText = `${selectedProducts.length} sản phẩm`;
    list.innerHTML = "";

    if (selectedProducts.length === 0) {
        list.innerHTML = `
            <div class="empty-selected-product">
                Chưa có sản phẩm nào trong đơn hàng
            </div>
        `;
        return;
    }

    list.innerHTML = `
        <div class="erp-table-wrapper">
            <div class="erp-table-header">
                <div>#</div>
                <div>Loại hoa</div>
                <div>Mã hoa</div>
                <div>DVT</div>
                <div>Quy cách bó</div>
                <div>Số lượng</div>
                <div>Ghi chú</div>
                <div>Thao tác</div>
            </div>
        </div>
    `;

    const table = list.querySelector(".erp-table-wrapper");

    selectedProducts.forEach((p, index) => {
        const qty =
            parseFloat(p.standard_quantity || 0) +
            parseFloat(p.sale_quantity || 0);

        table.insertAdjacentHTML("beforeend", `
            <div class="erp-table-row">
                <div>${index + 1}</div>

                <div>
                    <strong>${p.product_name}</strong>
                    <small>${p.display_type || "-"}</small>
                </div>

                <div>${p.product_code || "-"}</div>
                <div>${p.unit || "-"}</div>
                <div>${p.specification || "50"}</div>

                <div>
                    <strong>${qty}</strong>
                </div>

                <div>-</div>

                <div class="erp-action-cell">
                    <button type="button"
                            class="erp-action-btn edit"
                            onclick="editSelectedProduct(${index})">
                        <i class="bi bi-pencil-square"></i>
                    </button>

                    <button type="button"
                            class="erp-action-btn delete"
                            onclick="deleteSelectedProduct(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `);
    });
}
    


function renderHiddenProductInputs() {
    const box = document.getElementById("hiddenProductInputs");

    box.innerHTML = "";

    selectedProducts.forEach(p => {
        box.insertAdjacentHTML("beforeend", `
            <input type="hidden" name="lot_id[]" value="${p.lot_id || ""}">
            <input type="hidden" name="lot_code[]" value="${p.lot_code || ""}">
            <input type="hidden" name="product_code[]" value="${p.product_code || ""}">
            <input type="hidden" name="product_name[]" value="${p.product_name || ""}">
            <input type="hidden" name="flower_type[]" value="${p.flower_type || ""}">
            <input type="hidden" name="group_name[]" value="${p.group_name || ""}">
            <input type="hidden" name="unit[]" value="${p.unit || ""}">
            <input type="hidden" name="supplier_name[]" value="${p.supplier_name || ""}">
            <input type="hidden" name="standard_quantity[]" value="${p.standard_quantity || 0}">
            <input type="hidden" name="sale_quantity[]" value="${p.sale_quantity || 0}">
            <input type="hidden" name="specification[]" value="${p.specification || ""}">
        `);
    });

    console.log("hidden submit products:", selectedProducts);
}


function deleteSelectedProduct(index) {
    if (!confirm("Bạn có chắc muốn xóa sản phẩm này khỏi đơn hàng?")) return;

    selectedProducts.splice(index, 1);

    renderSelectedProducts();
    renderHiddenProductInputs();
}


function editSelectedProduct(index) {
    const p = selectedProducts[index];

    editingProductIndex = index;

    resetProductInputForm();
    const row = document.querySelector("#orderItemRows .order-item-row");

    row.querySelector(".flower-type-btn").innerText = p.display_type || "Chọn";
    row.querySelector(".flower-type-value").value = p.flower_type || "";

    row.querySelector('input[name="product_code[]"]').value = p.product_code;
    row.querySelector('input[name="product_name[]"]').value = p.product_name;
    row.querySelector('input[name="flower_type[]"]').value = p.flower_type;
    row.querySelector('input[name="group_name[]"]').value = p.group_name;
    row.querySelector('input[name="unit[]"]').value = p.unit;
    row.querySelector('input[name="supplier_name[]"]').value = p.supplier_name;
    row.querySelector('input[name="specification[]"]').value = p.specification;

    row.querySelector(".unit-display").value = p.unit;
    row.querySelector(".group-display").value = p.group_name;

    row.querySelector(".standard-input").value = p.standard_quantity;
    row.querySelector(".sale-input").value = p.sale_quantity;

    row.querySelector(".quantity-label").innerText = p.quantity_label;
    row.querySelector(".quantity-btn").innerText = p.quantity_text;

}


document.addEventListener("DOMContentLoaded", function () {
    addOrderItemRow();
});


function openQuantityBox(button) {
    const row = button.closest(".order-item-row");
    const productName = row.querySelector('input[name="product_name[]"]').value;

    if (!productName) {
        alert("Vui lòng chọn Tên Hoa/Lá phụ trước.");
        return;
    }

    currentQuantityRow = row;

    document.getElementById("stockProductName").innerText = productName;
    document.getElementById("stockStems").innerText = "Đang kiểm tra...";
    document.getElementById("stockBunches").innerText = "Đang kiểm tra...";
    document.getElementById("currentStockLimit").value = "999999";

    document.getElementById("modalStandardQty").value = "";
    document.getElementById("modalSaleQty").value = "";
    document.getElementById("modalStandardQty").disabled = false;
    document.getElementById("modalSaleQty").disabled = false;
    document.getElementById("quantityWarning").innerText = "";

    const modalEl = document.getElementById("quantityModal");
    const modal = new bootstrap.Modal(modalEl, {
        backdrop: false,
        keyboard: true
    });

    modal.show();

const productCode = row.querySelector('input[name="product_code[]"]').value || "";
const flowerType = row.querySelector('input[name="flower_type[]"]').value || "";

fetch(`/orders/api/stock/?product_code=${encodeURIComponent(productCode)}&product_name=${encodeURIComponent(productName)}&flower_type=${encodeURIComponent(flowerType)}`)
    .then(res => res.json())
    .then(data => {
        const selectedQty = getSelectedQuantityByProduct(productCode);
        const realStock = parseFloat(data.total_stems || 0);
        const availableStock = Math.max(realStock - selectedQty, 0);

        document.getElementById("stockStems").innerText = availableStock;
        document.getElementById("stockBunches").innerText = formatBunchBreakdown(availableStock);
        document.getElementById("currentStockLimit").value = availableStock;

        if (availableStock <= 0) {
            document.getElementById("quantityWarning").innerText =
                "Sản phẩm này đã được chọn hết tồn kho trong đơn hiện tại.";
        }
    })
    .catch(() => {
        document.getElementById("stockStems").innerText = "Lỗi kiểm tra";
        document.getElementById("stockBunches").innerText = "Lỗi kiểm tra";
        document.getElementById("currentStockLimit").value = "0";
    });
}

document.getElementById("modalStandardQty").addEventListener("input", function () {
    const standardQty = parseFloat(this.value || 0);
    const stockLimit = parseFloat(document.getElementById("currentStockLimit").value || 0);

    const row = currentQuantityRow;
    if (!row) return;

    const productCode = row.querySelector('input[name="product_code[]"]').value;
    const productName = row.querySelector('input[name="product_name[]"]').value;

    if (this.value) {
        document.getElementById("modalSaleQty").value = "";
        document.getElementById("modalSaleQty").disabled = true;
    } else {
        document.getElementById("modalSaleQty").disabled = false;
    }

    const missingQty = standardQty - stockLimit;

    if (missingQty > 0) {
        checkRawStockWarning(productCode, productName, missingQty);
    } else {
        document.getElementById("rawStockWarning").style.display = "none";
        document.getElementById("rawStockWarning").innerHTML = "";
    }
});


document.getElementById("modalSaleQty").addEventListener("input", function () {
    if (this.value) {
        document.getElementById("modalStandardQty").value = "";
        document.getElementById("modalStandardQty").disabled = true;
    } else {
        document.getElementById("modalStandardQty").disabled = false;
    }
});

document.getElementById("rawStockWarning").style.display = "none";
document.getElementById("rawStockWarning").innerHTML = "";

function applyQuantity() {
    if (!currentQuantityRow) return;

    const standardQty = parseFloat(document.getElementById("modalStandardQty").value || 0);
    const saleQty = parseFloat(document.getElementById("modalSaleQty").value || 0);
    const stockLimit = parseFloat(document.getElementById("currentStockLimit").value || 0);
    if (stockLimit <= 0) {
        warning.innerText = "Sản phẩm này đã hết tồn kho khả dụng.";
        return;
    }
    const warning = document.getElementById("quantityWarning");

    if (standardQty > 0 && saleQty > 0) {
        warning.innerText = "Chỉ được nhập Hoa tiêu chuẩn hoặc Hoa sale, không nhập cả hai.";
        return;
    }

    if (standardQty <= 0 && saleQty <= 0) {
        warning.innerText = "Vui lòng nhập số lượng.";
        return;
    }

    const selectedQty = standardQty > 0 ? standardQty : saleQty;

    if (selectedQty > stockLimit && saleQty > 0) {
        warning.innerText = "Hoa sale không được vượt quá tồn kho thành phẩm.";
        return;
    }

    const standardInput = currentQuantityRow.querySelector(".standard-input");
    const saleInput = currentQuantityRow.querySelector(".sale-input");
    const quantityBtn = currentQuantityRow.querySelector(".quantity-btn");
    const label = currentQuantityRow.querySelector(".quantity-label");

    if (standardQty > 0) {
        standardInput.value = standardQty;
        saleInput.value = 0;

        label.innerText = "SL Hoa tiêu chuẩn";
        quantityBtn.innerText = `Số Lượng: ${standardQty}`;
    }

    if (saleQty > 0) {
        saleInput.value = saleQty;
        standardInput.value = 0;

        label.innerText = "SL Hoa sale";
        quantityBtn.innerText = `Hoa sale: ${saleQty}`;
    }

    const modalEl = document.getElementById("quantityModal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
}



function openFlowerTypePopup(button) {
    currentFlowerTypeRow = button.closest(".order-item-row");

    const modal = new bootstrap.Modal(document.getElementById("flowerTypeModal"), {
        backdrop: false
    });

    modal.show();
}

function selectFlowerType(typeValue, typeLabel) {
    if (!currentFlowerTypeRow) return;

    const typeBtn =
        currentFlowerTypeRow.querySelector(".flower-type-btn");

    const typeInput =
        currentFlowerTypeRow.querySelector(".flower-type-value");

    const searchInput =
        currentFlowerTypeRow.querySelector(".flower-search-input");

    const suggestBox =
        currentFlowerTypeRow.querySelector(".flower-suggest-box");

    typeBtn.innerText = typeLabel;
    typeInput.value = typeValue;

    searchInput.value = "";
    suggestBox.innerHTML = "";
    suggestBox.style.display = "none";

    const modalEl = document.getElementById("flowerTypeModal");
    const modal = bootstrap.Modal.getInstance(modalEl);

    if (modal) {
        modal.hide();
    }
}


document.addEventListener("DOMContentLoaded", function () {addOrderItemRow();});

function getSelectedQuantityByProduct(productCode) {
    let total = 0;

    selectedProducts.forEach(p => {
        if (p.product_code === productCode) {
            total += parseFloat(p.standard_quantity || 0);
            total += parseFloat(p.sale_quantity || 0);
        }
    });

    return total;
}
function calculateBunchBreakdown(totalStems) {
    let remaining = parseFloat(totalStems || 0);

    const bunch100 = Math.floor(remaining / 100);
    remaining = remaining % 100;

    const bunch50 = Math.floor(remaining / 50);
    remaining = remaining % 50;

    const bunch30 = Math.floor(remaining / 30);
    remaining = remaining % 30;

    return {
        bunch100: bunch100,
        bunch50: bunch50,
        bunch30: bunch30,
        odd: remaining
    };
}


function formatBunchBreakdown(totalStems) {
    const b = calculateBunchBreakdown(totalStems);

    let text = [];

    if (b.bunch100 > 0) text.push(`${b.bunch100} bó 100c`);
    if (b.bunch50 > 0) text.push(`${b.bunch50} bó 50c`);
    if (b.bunch30 > 0) text.push(`${b.bunch30} bó 30c`);
    if (b.odd > 0) text.push(`lẻ ${b.odd}c`);

    if (text.length === 0) return "0 bó";

    return text.join(", ");
}

function checkRawStockWarning(productCode, productName, missingQty) {
    const warningBox = document.getElementById("rawStockWarning");

    warningBox.style.display = "none";
    warningBox.innerHTML = "";

    if (missingQty <= 0) return;

    fetch(`/orders/api/raw-stock/?product_code=${productCode}&product_name=${productName}&required_qty=${missingQty}`)
        .then(res => res.json())
        .then(data => {
            if (data.raw_available > 0) {
                if (data.still_missing_qty > 0) {
                    warningBox.innerHTML = `
                        <i class="bi bi-exclamation-triangle-fill"></i>
                        Thành phẩm đang thiếu <strong>${missingQty}c</strong>.
                        Kho nguyên liệu còn <strong>${data.raw_available}c</strong>,
                        có thể sơ chế thêm <strong>${data.can_process_qty}c</strong>,
                        vẫn còn thiếu <strong>${data.still_missing_qty}c</strong>.
                    `;
                } else {
                    warningBox.innerHTML = `
                        <i class="bi bi-tools"></i>
                        Thành phẩm đang thiếu <strong>${missingQty}c</strong>.
                        Kho nguyên liệu còn <strong>${data.raw_available}c</strong>.
                        Cần yêu cầu sơ chế thêm <strong>${data.can_process_qty}c</strong> để đủ đơn.
                    `;
                }

                warningBox.style.display = "block";
            }
        });
}
document.addEventListener("DOMContentLoaded", function () {
    const orderForm = document.querySelector("#createOrderModal form");

    if (orderForm) {
        orderForm.addEventListener("submit", function () {
            renderHiddenProductInputs();

            document.querySelectorAll("#orderItemRows [name]").forEach(input => {
                input.disabled = true;
            });

            console.log("SUBMIT FINAL PRODUCTS:", selectedProducts);
        });
    }
});


function searchFlowerSuggest(input) {
    const row = input.closest(".order-item-row");
    const box = row.querySelector(".flower-suggest-box");
    const q = input.value.trim();

    if (q.length < 1) {
        box.innerHTML = "";
        box.style.display = "none";
        return;
    }

    const flowerType = row.querySelector(".flower-type-value").value || "";

    fetch(`/orders/api/flowers/?type=${flowerType}&q=${encodeURIComponent(q)}`)
        .then(res => res.json())
        .then(data => {
            box.innerHTML = "";

            if (!data.flowers || data.flowers.length === 0) {
                box.innerHTML = `
                    <div class="flower-suggest-empty">
                        Không tìm thấy sản phẩm
                    </div>
                `;
                box.style.display = "block";
                return;
            }

            data.flowers.forEach(f => {
                const item = document.createElement("div");
                item.className = "flower-suggest-item";

                item.innerHTML = `
                    <strong>${f.name}</strong>
                    <span>${f.code || "-"} | Lô: ${f.lot_code || "-"} | Tồn: ${f.total_stems || 0} cành</span>
                    <small>${f.supplier || "-"} | ${f.unit || "-"} | ${f.group_name || "-"}</small>
                `;

                item.onclick = function () {
                    fillFlowerInfoFromSuggest(row, f);
                    input.value = f.name;
                    box.innerHTML = "";
                    box.style.display = "none";
                };

                box.appendChild(item);
            });

            box.style.display = "block";
        });
}

function fillFlowerInfoFromSuggest(row, data) {
    row.querySelector('input[name="product_code[]"]').value = data.code || "";
    row.querySelector('input[name="product_name[]"]').value = data.name || "";
    row.querySelector('input[name="flower_type[]"]').value = data.category || "";
    row.querySelector('input[name="group_name[]"]').value = data.group_name || "";
    row.querySelector('input[name="unit[]"]').value = data.unit || "";
    row.querySelector('input[name="supplier_name[]"]').value = data.supplier || "";
    row.querySelector('input[name="lot_id[]"]').value = data.lot_id || "";
    row.querySelector('input[name="lot_code[]"]').value = data.lot_code || "";

    row.querySelector(".unit-display").value = data.unit || "";
    row.querySelector(".group-display").value = data.group_name || "";
}