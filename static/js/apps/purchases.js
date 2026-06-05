let purchaseQueue = [];
let editingIndex = null;

function setPurchaseOrderNow() {
    const input = document.getElementById("purchaseOrderDateTime");
    if (!input) return;

    const now = new Date();
    const offset = now.getTimezoneOffset();
    const local = new Date(now.getTime() - offset * 60000);

    input.value = local.toISOString().slice(0, 16);
}

function getSelectedPurchaseGroup() {
    const checked = document.querySelector('input[name="purchase_group"]:checked');
    return checked ? checked.value : "HH";
}

function getCurrentSupplierValue() {
    const supplierInput = document.querySelector('input[name="supplier"]');
    return supplierInput ? supplierInput.value.trim() : "";
}

function getSupplierShortName(supplierValue) {
    if (!supplierValue) return "-";

    if (supplierValue.includes(" - ")) {
        return supplierValue.split(" - ")[1] || supplierValue;
    }

    return supplierValue;
}

function shouldShowSupplierColumn() {
    const suppliers = purchaseQueue
        .map(item => item.supplier || "")
        .filter(value => value);

    const uniqueSuppliers = [...new Set(suppliers)];

    return uniqueSuppliers.length > 1;
}

function refreshPurchaseProductDatalist() {
    const list = document.getElementById("purchaseProductList");
    if (!list) return;

    const group = getSelectedPurchaseGroup();

    list.innerHTML = PURCHASE_PRODUCTS
        .filter(product => product.category_type === group)
        .map(product => `<option value="${product.code} - ${product.name}"></option>`)
        .join("");
}

function handlePurchaseEntryProductInput(input) {
    const value = input.value.trim();

    const product = PURCHASE_PRODUCTS.find(function(item) {
        return `${item.code} - ${item.name}` === value;
    });

    document.getElementById("purchaseProductCode").value = product ? product.code : "";
    document.getElementById("purchaseProductUnit").value = product ? (product.unit || "cành") : "cành";
}

function resetPurchaseEntryForm() {
    document.getElementById("purchaseProductInput").value = "";
    document.getElementById("purchaseProductCode").value = "";
    document.getElementById("purchaseProductUnit").value = "cành";
    document.getElementById("purchaseStemsPerBundle").value = "50";
    document.getElementById("purchaseOrderedQuantity").value = "0";
    document.getElementById("purchaseItemNote").value = "";

    editingIndex = null;
}

function addPurchaseItemToQueue() {
    const group = getSelectedPurchaseGroup();
    const supplierValue = getCurrentSupplierValue();

    if (!supplierValue) {
        alert("Vui lòng chọn Nhà cung cấp / Khách hàng cung cấp trước khi thêm sản phẩm.");
        return;
    }

    const productValue = document.getElementById("purchaseProductInput").value.trim();

    const product = PURCHASE_PRODUCTS.find(function(item) {
        return `${item.code} - ${item.name}` === productValue;
    });

    if (!product) {
        alert("Vui lòng chọn đúng loại hoa từ gợi ý.");
        return;
    }

    const orderedQuantity = Number(document.getElementById("purchaseOrderedQuantity").value || 0);

    if (orderedQuantity <= 0) {
        alert("Vui lòng nhập số lượng lớn hơn 0.");
        return;
    }

    let stemsPerBundle = 0;

    if (group === "HH") {
        stemsPerBundle = Number(document.getElementById("purchaseStemsPerBundle").value || 50);
    }

    const item = {
        supplier: supplierValue,
        product_group: group,
        product_code: product.code,
        product_name: product.name,
        unit: document.getElementById("purchaseProductUnit").value || "cành",
        stems_per_bundle: stemsPerBundle,
        ordered_quantity: orderedQuantity,
        note: document.getElementById("purchaseItemNote").value || ""
    };

    if (editingIndex !== null) {
        purchaseQueue[editingIndex] = item;
    } else {
        purchaseQueue.push(item);
    }

    renderPurchaseQueue();
    resetPurchaseEntryForm();
}

function renderPurchaseQueue() {
    const body = document.getElementById("purchaseQueueBody");
    const table = document.querySelector(".purchase-queue-table");

    if (!body) return;

    const showSupplier = shouldShowSupplierColumn();
    const colSpan = showSupplier ? 9 : 8;

    if (table) {
        const thead = table.querySelector("thead tr");

        if (thead) {
            thead.innerHTML = `
                <th style="width:48px;">#</th>
                ${showSupplier ? "<th>Nhà cung cấp</th>" : ""}
                <th>Loại hoa</th>
                <th>Mã hoa</th>
                <th>ĐVT</th>
                <th>Quy cách bó</th>
                <th>Số lượng</th>
                <th>Ghi chú</th>
                <th style="width:110px;">Thao tác</th>
            `;
        }
    }

    if (purchaseQueue.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="${colSpan}" class="text-center text-muted py-4">
                    Chưa có sản phẩm nào trong đơn đặt mua
                </td>
            </tr>
        `;
        return;
    }

    body.innerHTML = purchaseQueue.map(function(item, index) {
        return `
            <tr>
                <td>${index + 1}</td>

                ${
                    showSupplier
                        ? `<td>
                            <div class="item-name">${getSupplierShortName(item.supplier)}</div>
                            <div class="item-group">${item.supplier || "-"}</div>
                           </td>`
                        : ""
                }

                <td>
                    <div class="item-name">${item.product_name}</div>
                    <div class="item-group">${item.product_group}</div>
                </td>

                <td>${item.product_code}</td>
                <td>${item.unit}</td>
                <td>${item.product_group === "HH" ? item.stems_per_bundle : "-"}</td>
                <td><strong>${item.ordered_quantity}</strong></td>
                <td>${item.note || "-"}</td>

                <td>
                    <button type="button" class="btn btn-sm btn-light" onclick="editPurchaseQueueItem(${index})">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-light text-danger" onclick="removePurchaseQueueItem(${index})">
                        <i class="bi bi-trash3"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function editPurchaseQueueItem(index) {
    const item = purchaseQueue[index];
    editingIndex = index;

    const supplierInput = document.querySelector('input[name="supplier"]');
    if (supplierInput && item.supplier) {
        supplierInput.value = item.supplier;
    }

    const groupInput = document.querySelector(`input[name="purchase_group"][value="${item.product_group}"]`);
    if (groupInput) {
        groupInput.checked = true;
        refreshPurchaseProductDatalist();
    }

    document.getElementById("purchaseProductInput").value = `${item.product_code} - ${item.product_name}`;
    document.getElementById("purchaseProductCode").value = item.product_code;
    document.getElementById("purchaseProductUnit").value = item.unit;
    document.getElementById("purchaseStemsPerBundle").value = item.stems_per_bundle || 50;
    document.getElementById("purchaseOrderedQuantity").value = item.ordered_quantity;
    document.getElementById("purchaseItemNote").value = item.note || "";

    syncPurchaseGroupButtonUI();
}

function removePurchaseQueueItem(index) {
    purchaseQueue.splice(index, 1);
    renderPurchaseQueue();
}

function collectPurchaseItems() {
    const input = document.getElementById("purchaseItemsJson");
    if (!input) return false;

    input.value = JSON.stringify(purchaseQueue);
    return purchaseQueue.length > 0;
}

function syncPurchaseGroupButtonUI() {
    document.querySelectorAll(".purchase-type-option").forEach(item => {
        item.classList.remove("btn-success", "text-white");
        item.classList.add("btn-light");
    });

    const checked = document.querySelector('input[name="purchase_group"]:checked');

    if (checked) {
        const label = checked.closest(".purchase-type-option");
        if (label) {
            label.classList.add("btn-success", "text-white");
            label.classList.remove("btn-light");
        }
    }

    const group = getSelectedPurchaseGroup();
    const stemWrap = document.getElementById("purchaseStemRuleWrap");

    if (stemWrap) {
        if (group === "HH") {
            stemWrap.classList.remove("d-none");
        } else {
            stemWrap.classList.add("d-none");
        }
    }
}

function setupPurchaseGroupButtons() {
    document.querySelectorAll(".purchase-type-option").forEach(function(label) {
        label.addEventListener("click", function() {
            const input = label.querySelector("input");
            input.checked = true;

            syncPurchaseGroupButtonUI();
            refreshPurchaseProductDatalist();
            resetPurchaseEntryForm();
        });
    });

    syncPurchaseGroupButtonUI();
}

function setupDriverAutoFill() {
    const driverInput = document.getElementById("driverNameInput");
    const driverCodeInput = document.getElementById("driverCodeInput");

    if (!driverInput || !driverCodeInput) return;

    driverInput.addEventListener("input", function() {
        const found = PURCHASE_DRIVERS.find(driver => driver.name === driverInput.value);
        driverCodeInput.value = found ? found.code : "";
    });
}

function setupVehicleTypeBehavior() {
    const vehicleSelect = document.getElementById("vehicleInfoSelect");
    const driverNameLabel = document.getElementById("driverNameLabel");
    const driverCodeLabel = document.getElementById("driverCodeLabel");
    const driverCodeInput = document.getElementById("driverCodeInput");

    if (!vehicleSelect) return;

    vehicleSelect.addEventListener("change", function() {
        if (vehicleSelect.value.includes("Khách lẻ")) {
            driverNameLabel.innerText = "Khách lẻ giao";
            driverCodeLabel.innerText = "Thông tin khách lẻ";
            driverCodeInput.readOnly = false;
            driverCodeInput.value = "";
        } else {
            driverNameLabel.innerText = "Tên tài xế";
            driverCodeLabel.innerText = "Mã NV tài xế";
            driverCodeInput.readOnly = true;
            driverCodeInput.value = "";
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    setupPurchaseGroupButtons();
    setupDriverAutoFill();
    setupVehicleTypeBehavior();

    refreshPurchaseProductDatalist();
    setPurchaseOrderNow();
    renderPurchaseQueue();

    const form = document.querySelector("#purchaseOrderModal form");

    if (form) {
        form.addEventListener("submit", function(event) {
            const ok = collectPurchaseItems();

            if (!ok) {
                event.preventDefault();
                alert("Vui lòng thêm ít nhất một sản phẩm vào hàng đợi.");
            }
        });
    }
});