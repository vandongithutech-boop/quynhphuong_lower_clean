let currentProducts = [];
let receiptItems = [];
let editingIndex = null;

const productList = document.getElementById("productList");
const productInput = document.getElementById("productInput");
const unitInput = document.getElementById("unitInput");
const gradeInput = document.getElementById("gradeInput");
const quantityInput = document.getElementById("quantityInput");
const receiptItemsBox = document.getElementById("receiptItems");
const itemsJson = document.getElementById("itemsJson");
const itemCountText = document.getElementById("itemCountText");

document.querySelectorAll(".product-group-radio").forEach(radio => {
    radio.addEventListener("change", function () {
        if (this.value === "HH") currentProducts = productsHH;
        if (this.value === "HP") currentProducts = productsHP;
        if (this.value === "VT") currentProducts = productsVT;

        loadProductOptions();
        clearProductForm();
    });
});

if (productInput) {
    productInput.addEventListener("input", function () {
        const selected = findSelectedProduct();
        unitInput.value = selected ? selected.unit : "";
    });
}

function loadProductOptions() {
    productList.innerHTML = "";

    currentProducts.forEach(product => {
        const option = document.createElement("option");
        option.value = `${product.code} - ${product.name}`;
        productList.appendChild(option);
    });
}

function findSelectedProduct() {
    const value = productInput.value;

    return currentProducts.find(product => {
        return `${product.code} - ${product.name}` === value;
    });
}

function addProductToReceipt() {
    const selectedProduct = findSelectedProduct();
    const grade = gradeInput.value.trim();
    const quantity = quantityInput.value;

    if (!selectedProduct) {
        alert("Vui lòng chọn sản phẩm hợp lệ.");
        return;
    }

    if (!quantity || Number(quantity) <= 0) {
        alert("Vui lòng nhập số lượng hợp lệ.");
        return;
    }

    const item = {
        product_code: selectedProduct.code,
        product_name: selectedProduct.name,
        unit: selectedProduct.unit,
        flower_grade: grade,
        quantity: quantity
    };

    if (editingIndex !== null) {
        receiptItems[editingIndex] = item;
        editingIndex = null;
    } else {
        receiptItems.push(item);
    }

    renderReceiptItems();
    clearProductForm();
}

function renderReceiptItems() {
    receiptItemsBox.innerHTML = "";

    if (receiptItems.length === 0) {
        receiptItemsBox.innerHTML = `
            <div class="empty-state py-4">
                Chưa có sản phẩm nào trong phiếu nhập
            </div>
        `;
    } else {
        receiptItems.forEach((item, index) => {
            const row = document.createElement("div");
            row.className = "receipt-item-card";

            row.innerHTML = `
                <div class="receipt-product-card">
                    <div class="receipt-product-main">
                        <div class="d-flex align-items-center gap-2 mb-2">
                            <span class="receipt-code-badge">${item.product_code}</span>
                            <span class="receipt-group-badge">${document.querySelector('input[name="product_group"]:checked')?.value || ""}</span>
                        </div>

                        <div class="receipt-name">${item.product_name}</div>
                        <div class="receipt-sub">Sản phẩm nhập kho</div>
                    </div>

                    <div class="receipt-info">
                        <div class="receipt-label">Đơn vị tính</div>
                        <div class="receipt-value">${item.unit || "-"}</div>

                        <div class="receipt-label mt-3">Độ hoa</div>
                        <div class="receipt-empty">${item.flower_grade || "chưa có dữ liệu"}</div>
                    </div>

                    <div class="receipt-info">
                        <div class="receipt-label">Số lượng</div>
                        <div class="receipt-value">${item.quantity}</div>
                    </div>

                    <div class="action-icon-group">
                        <button type="button" class="action-icon-btn edit" onclick="editReceiptItem(${index})">
                            <i class="bi bi-pencil-square"></i>
                        </button>

                        <button type="button" class="action-icon-btn delete" onclick="deleteReceiptItem(${index})">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                </div>
            `;

            receiptItemsBox.appendChild(row);
        });
    }

    itemCountText.innerText = `${receiptItems.length} sản phẩm`;
    itemsJson.value = JSON.stringify(receiptItems);
}

function editReceiptItem(index) {
    const item = receiptItems[index];

    productInput.value = `${item.product_code} - ${item.product_name}`;
    unitInput.value = item.unit;
    gradeInput.value = item.flower_grade;
    quantityInput.value = item.quantity;

    editingIndex = index;
}

function deleteReceiptItem(index) {
    if (confirm("Bạn có chắc muốn xóa sản phẩm này khỏi phiếu nhập?")) {
        receiptItems.splice(index, 1);
        renderReceiptItems();
    }
}

function clearProductForm() {
    productInput.value = "";
    unitInput.value = "";
    gradeInput.value = "";
    quantityInput.value = "";
    editingIndex = null;
}

function clearSupplier() {
    const input = document.getElementById("supplierInput");

    if (!input) return;

    input.value = "";
    input.dataset.code = "";
    input.dataset.name = "";

    if (window.LiquidSuggest) {
        window.LiquidSuggest.close();
    }

    input.focus();
}

function clearProduct() {
    productInput.value = "";
    unitInput.value = "";
}

function clearGrade() {
    gradeInput.value = "";
}

function clearQuantity() {
    quantityInput.value = "";
}

if (document.getElementById("stockInForm")) {
    document.getElementById("stockInForm").addEventListener("submit", function (e) {
        if (receiptItems.length === 0) {
            e.preventDefault();
            alert("Vui lòng thêm ít nhất một sản phẩm vào phiếu nhập.");
            return;
        }

        const groupChecked = document.querySelector('input[name="product_group"]:checked');

        if (!groupChecked) {
            e.preventDefault();
            alert("Vui lòng chọn nhóm hàng nhập.");
        }
    });
}

/* =========================
   XUẤT KHO
========================= */

let stockOutProducts = [];
let stockOutItems = [];
let selectedStockOutType = "";

const stockOutProductList = document.getElementById("stockOutProductList");
const stockOutProductInput = document.getElementById("stockOutProductInput");
const stockOutUnitInput = document.getElementById("stockOutUnitInput");
const stockOutGradeInput = document.getElementById("stockOutGradeInput");
const stockOutAvailableInput = document.getElementById("stockOutAvailableInput");
const stockOutQuantityInput = document.getElementById("stockOutQuantityInput");
const stockOutSupplierInput = document.getElementById("stockOutSupplierInput");
const stockOutReasonSelect = document.getElementById("stockOutReasonSelect");
const stockOutOtherReasonBox = document.getElementById("stockOutOtherReasonBox");
const stockOutOtherReasonInput = document.getElementById("stockOutOtherReasonInput");
const stockOutItemsBox = document.getElementById("stockOutItems");
const stockOutItemsJson = document.getElementById("stockOutItemsJson");
const stockOutItemCountText = document.getElementById("stockOutItemCountText");

document.querySelectorAll(".stock-out-type-radio").forEach(radio => {
    radio.addEventListener("change", function () {
        selectedStockOutType = this.value;
        loadStockOutProducts(selectedStockOutType);
        clearStockOutProduct();
    });
});

function loadStockOutProducts(type) {
    if (!stockOutProductList) return;

    stockOutProducts = [];
    stockOutProductList.innerHTML = "";

    fetch(`/inventory/api/xuat-kho/products/?type=${type}`)
        .then(res => res.json())
        .then(data => {
            stockOutProducts = data.products || [];

            stockOutProducts.forEach(p => {
                const option = document.createElement("option");
                option.value = `${p.stock_id} - ${p.product_name} - ${p.lot_code} - Tồn ${p.quantity}`;
                stockOutProductList.appendChild(option);
            });
        });
}

function findSelectedStockOutProduct() {
    const value = stockOutProductInput.value;

    return stockOutProducts.find(p => {
        return `${p.stock_id} - ${p.product_name} - ${p.lot_code} - Tồn ${p.quantity}` === value;
    });
}

if (stockOutProductInput) {
    stockOutProductInput.addEventListener("input", function () {
        const selected = findSelectedStockOutProduct();

        if (!selected) {
            stockOutUnitInput.value = "";
            stockOutGradeInput.value = "";
            stockOutAvailableInput.value = "";
            stockOutSupplierInput.value = "";
            return;
        }

        stockOutUnitInput.value = selected.unit || "";
        stockOutGradeInput.value = selected.flower_grade || "";
        stockOutAvailableInput.value = selected.quantity || 0;
        stockOutSupplierInput.value = selected.supplier_name || "";
    });
}

if (stockOutReasonSelect) {
    stockOutReasonSelect.addEventListener("change", function () {
        if (this.value === "Khác") {
            stockOutOtherReasonBox.classList.remove("d-none");
        } else {
            stockOutOtherReasonBox.classList.add("d-none");
            stockOutOtherReasonInput.value = "";
        }
    });
}

function addProductToStockOut() {
    const selected = findSelectedStockOutProduct();

    if (!selected) {
        alert("Vui lòng chọn sản phẩm hợp lệ.");
        return;
    }

    const quantity = parseFloat(stockOutQuantityInput.value || 0);
    const available = parseFloat(selected.quantity || 0);

    if (quantity <= 0) {
        alert("Vui lòng nhập số lượng xuất.");
        return;
    }

    if (quantity > available) {
        alert(`Số lượng xuất không được vượt tồn kho. Tồn hiện tại: ${available}`);
        return;
    }

    if (quantity > 1000) {
        const ok = confirm(`Bạn có chắc chắn chuyển ${quantity} không?`);
        if (!ok) return;
    }

    let reason = stockOutReasonSelect.value;

    if (reason === "Khác") {
        reason = stockOutOtherReasonInput.value.trim();

        if (!reason) {
            alert("Vui lòng nhập lý do khác.");
            return;
        }
    }

    if (!reason) {
        alert("Vui lòng chọn lý do Sale/Hủy.");
        return;
    }

    const item = {
        stock_out_type: selectedStockOutType,
        stock_id: selected.stock_id,
        lot_id: selected.lot_id,
        lot_code: selected.lot_code,
        warehouse_type: selected.warehouse_type,
        product_group: selected.product_group,
        product_code: selected.product_code,
        product_name: selected.product_name,
        unit: selected.unit,
        original_grade: selected.flower_grade,
        output_grade: stockOutGradeInput.value.trim(),
        supplier_code: selected.supplier_code,
        supplier_name: selected.supplier_name,
        received_date: selected.received_date,
        available_quantity: available,
        quantity: quantity,
        reason: reason,
    };

    stockOutItems.push(item);

    renderStockOutItems();
    clearStockOutProduct();
}

function renderStockOutItems() {
    stockOutItemsBox.innerHTML = "";

    if (stockOutItems.length === 0) {
        stockOutItemsBox.innerHTML = `
            <div class="empty-state py-4">
                Chưa có sản phẩm nào trong phiếu xuất
            </div>
        `;
    } else {
        stockOutItems.forEach((item, index) => {
            const row = document.createElement("div");
            row.className = "receipt-item-card";

            row.innerHTML = `
                <div class="receipt-product-card">
                    <div class="receipt-product-main">
                        <div class="d-flex align-items-center gap-2 mb-2">
                            <span class="receipt-code-badge">${item.product_code}</span>
                            <span class="receipt-group-badge">${item.lot_code}</span>
                        </div>

                        <div class="receipt-name">${item.product_name}</div>
                        <div class="receipt-sub">
                            ${item.warehouse_type} → ${getStockOutDestination(item.stock_out_type)}
                        </div>
                    </div>

                    <div class="receipt-info">
                        <div class="receipt-label">NCC</div>
                        <div class="receipt-value">${item.supplier_name || "-"}</div>

                        <div class="receipt-label mt-3">Lý do</div>
                        <div class="receipt-empty">${item.reason}</div>
                    </div>

                    <div class="receipt-info">
                        <div class="receipt-label">Số lượng</div>
                        <div class="receipt-value">${item.quantity}</div>

                        <div class="receipt-label mt-3">Độ xuất</div>
                        <div class="receipt-empty">${item.output_grade || "-"}</div>
                    </div>

                    <div class="action-icon-group">
                        <button type="button" class="action-icon-btn delete" onclick="deleteStockOutItem(${index})">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                </div>
            `;

            stockOutItemsBox.appendChild(row);
        });
    }

    stockOutItemCountText.innerText = `${stockOutItems.length} sản phẩm`;
    stockOutItemsJson.value = JSON.stringify(stockOutItems);
}

function getStockOutDestination(type) {
    if (type === "HH" || type === "HP" || type === "DIRECT_SALE") {
        return "SALE";
    }

    if (type === "DAMAGED") {
        return "DAMAGED";
    }

    return "-";
}

function deleteStockOutItem(index) {
    if (!confirm("Bạn có chắc muốn xóa sản phẩm này khỏi phiếu xuất?")) return;

    stockOutItems.splice(index, 1);
    renderStockOutItems();
}

function clearStockOutProduct() {
    stockOutProductInput.value = "";
    stockOutUnitInput.value = "";
    stockOutGradeInput.value = "";
    stockOutAvailableInput.value = "";
    stockOutQuantityInput.value = "";
    stockOutSupplierInput.value = "";
    stockOutReasonSelect.value = "";
    stockOutOtherReasonInput.value = "";
    stockOutOtherReasonBox.classList.add("d-none");
}

if (document.getElementById("stockOutForm")) {
    document.getElementById("stockOutForm").addEventListener("submit", function (e) {
        if (stockOutItems.length === 0) {
            e.preventDefault();
            alert("Vui lòng thêm ít nhất một sản phẩm vào phiếu xuất.");
            return;
        }

        stockOutItemsJson.value = JSON.stringify(stockOutItems);
    });
}

/* =========================
   REALTIME ĐƠN VẬN CHUYỂN → KHO TỔNG
   Chỉ thêm đơn mới, không render lại đơn đã có
========================= */

function renderPendingStockInOrders(orders) {
    const box = document.getElementById("pendingStockInOrdersBox");

    if (!box) return;

    if (!orders || orders.length === 0) {
        if (box.querySelectorAll(".transport-po-card").length === 0) {
            box.innerHTML = `
                <div class="text-center py-5 pending-empty-state">
                    <i class="bi bi-box-seam" style="font-size:64px;color:#d1d5db;"></i>
                    <h5 class="fw-bold mt-3">Chưa có đơn vận chuyển chờ nhập kho</h5>
                    <div class="text-muted">
                        Khi tài xế hoàn thành vận chuyển, đơn sẽ xuất hiện tại đây.
                    </div>
                </div>
            `;
        }

        return;
    }

    const emptyState = box.querySelector(".pending-empty-state");
    if (emptyState) {
        emptyState.remove();
    }

    orders.forEach(po => {
        const existedCard = box.querySelector(`[data-po-id="${po.id}"]`);

        if (existedCard) {
            return;
        }

        const itemRows = po.items.map((item, index) => {
            return `
                <tr>
                    <td>${index + 1}</td>

                    <td class="fw-bold">${item.product_name}</td>

                    <td>${item.product_code}</td>

                    <td class="supplier-col">${item.supplier_name || "-"}</td>

                    <td>${item.unit || "cành"}</td>

                    <td class="text-center">
                        <input type="number"
                            name="stems_per_bundle_${item.id}"
                            class="form-control form-control-sm text-center warehouse-bundle-input"
                            data-item-id="${item.id}"
                            value="${item.stems_per_bundle || 50}"
                            min="1">
                    </td>

                    <td class="text-end fw-bold">${item.ordered_quantity}</td>

                    <td class="text-end fw-bold">${item.driver_received_quantity}</td>

                    <td>
                        <input type="number"
                            name="stock_in_qty_${item.id}"
                            class="form-control form-control-sm warehouse-check-input"
                            data-item-id="${item.id}"
                            value="${item.warehouse_checked_quantity}"
                            min="0"
                            step="0.01">
                    </td>

                    <td>
                        ${item.note ? item.note : '<span class="empty-data">không có</span>'}
                    </td>
                </tr>
            `;
        }).join("");

        const cardHtml = `
            <div class="transport-po-card" data-po-id="${po.id}">
                <form method="post" action="/inventory/tao-qr-bo-tu-don/${po.id}/">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">

                    <div class="transport-po-header inventory-po-header">
                        <div>
                            <div class="transport-supplier-name">
                                ${po.supplier_display || "-"}
                            </div>

                            <div class="transport-po-code">
                                ${po.po_code || "-"}
                            </div>
                        </div>

                        <div class="inventory-approval-step">
                            <div class="info-label">Người đặt hàng</div>
                            <div class="info-value">Kinh doanh / Kế toán</div>

                            <div class="approval-check-icon">
                                <i class="bi bi-check2"></i>
                            </div>
                        </div>

                        <div class="inventory-approval-step">
                            <div class="info-label">Tài xế xác nhận</div>
                            <div class="info-value">${po.driver_name}</div>

                            <div class="approval-check-icon">
                                <i class="bi bi-check2"></i>
                            </div>
                        </div>

                        <div>
                            <div class="info-label">Phương tiện</div>
                            <div class="info-value">${po.vehicle_info}</div>
                        </div>

                        <div class="transport-po-actions text-center">
                            <div class="driver-confirmed-box">
                                <div class="driver-confirmed-icon pending">
                                    <i class="bi bi-hourglass-split"></i>
                                </div>

                                <div class="driver-confirmed-time">
                                    Chờ kho nhận
                                </div>
                            </div>

                            <div class="mt-2">
                                <span class="status-pill">
                                    ${po.status_display}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="transport-po-items mt-3">
                        <div class="table-responsive purchase-queue-table-wrap">
                            <table class="table align-middle mb-0 purchase-queue-table">
                                <thead>
                                    <tr>
                                        <th style="width:48px;">#</th>
                                        <th>Loại hoa</th>
                                        <th>Mã hoa</th>
                                        <th>Nhà cung cấp</th>
                                        <th>ĐVT</th>
                                        <th>Quy cách bó</th>
                                        <th>SL đặt</th>
                                        <th>SL tài xế nhận</th>
                                        <th>SL kho kiểm</th>
                                        <th>Ghi chú</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    ${itemRows}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="text-end mt-3">
                        <button type="submit" class="btn btn-success">
                            <i class="bi bi-qr-code"></i>
                            Tạo QR bó
                        </button>
                    </div>
                </form>
            </div>
        `;

        box.insertAdjacentHTML("afterbegin", cardHtml);
    });
}

function refreshPendingStockInOrders() {
    fetch("/inventory/api/pending-stock-in-orders/")
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderPendingStockInOrders(data.orders);
            }
        })
        .catch(() => {});
}

function getCSRFToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');

    if (input) {
        return input.value;
    }

    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookie ? cookie.split("=")[1] : "";
}

setInterval(() => {
    refreshPendingStockInOrders();
}, 10000);

document.addEventListener("change", function (e) {
    const isQtyInput = e.target.classList.contains("warehouse-check-input");
    const isBundleInput = e.target.classList.contains("warehouse-bundle-input");

    if (!isQtyInput && !isBundleInput) return;

    const itemId = e.target.dataset.itemId;

    const qtyInput = document.querySelector(
        `.warehouse-check-input[data-item-id="${itemId}"]`
    );

    const bundleInput = document.querySelector(
        `.warehouse-bundle-input[data-item-id="${itemId}"]`
    );

    fetch("/inventory/api/save-warehouse-check/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: qtyInput ? qtyInput.value : 0,
            stems_per_bundle: bundleInput ? bundleInput.value : 50,
        })
    });
});

/* ===============================
   KIỂM KÊ NHANH KHO TỔNG
================================ */

let quickCheckProducts = [];
let quickCheckItems = [];

const quickCheckProductInput = document.getElementById("checkProductInput");
const quickCheckProductList = document.getElementById("checkProductList");
const quickCheckProductCodeInput = document.getElementById("checkProductCodeInput");
const quickCheckUnitInput = document.getElementById("checkUnitInput");
const quickCheckCurrentStockInput = document.getElementById("checkCurrentStockInput");
const quickCheckQuantityInput = document.querySelector("input[name='check_quantity']");
const quickCheckItemsTable = document.getElementById("quickCheckItemsTable");
const quickCheckItemsJson = document.getElementById("quickCheckItemsJson");
const quickCheckItemCountText = document.getElementById("quickCheckItemCountText");
const quickInventoryModal = document.getElementById("quickInventoryCheckModal");
const saleTypeBox = document.getElementById("saleTypeBox");

function getQuickCheckProductsByGroup(group) {
    if (group === "HH") return window.productsHH || [];
    if (group === "HP") return window.productsHP || [];
    if (group === "VT") return window.productsVT || [];
    return [];
}

function resetQuickCheckProductFields() {
    if (quickCheckProductInput) quickCheckProductInput.value = "";
    if (quickCheckProductCodeInput) quickCheckProductCodeInput.value = "";
    if (quickCheckUnitInput) quickCheckUnitInput.value = "";
    if (quickCheckCurrentStockInput) quickCheckCurrentStockInput.value = "0";
    if (quickCheckQuantityInput) quickCheckQuantityInput.value = "";
}

function resetQuickCheckSaleType() {
    document.querySelectorAll('input[name="check_sale_type"]').forEach(function (radio) {
        radio.checked = false;
    });
}

function loadQuickCheckProductOptions(group) {
    if (!quickCheckProductList) return;

    quickCheckProducts = getQuickCheckProductsByGroup(group);
    quickCheckProductList.innerHTML = "";

    quickCheckProducts.forEach(function (product) {
        const option = document.createElement("option");
        option.value = `${product.code} - ${product.name}`;
        quickCheckProductList.appendChild(option);
    });
}

function findQuickCheckSelectedProduct() {
    if (!quickCheckProductInput) return null;

    const value = quickCheckProductInput.value.trim();

    return quickCheckProducts.find(function (product) {
        return value === `${product.code} - ${product.name}` ||
               value === product.name ||
               value === product.code;
    });
}

document.querySelectorAll(".check-product-group-radio").forEach(function (radio) {
    radio.addEventListener("change", function () {
        loadQuickCheckProductOptions(this.value);
        resetQuickCheckProductFields();
    });
});

document.querySelectorAll('input[name="check_warehouse_type"]').forEach(function (radio) {
    radio.addEventListener("change", function () {
        if (!saleTypeBox) return;

        const saleTypeBoxLabel = document.getElementById("saleTypeBoxLabel");

        if (this.value === "SALE" || this.value === "DAMAGED") {
        saleTypeBox.classList.remove("d-none");

        if (saleTypeBoxLabel) {
            if (this.value === "SALE") {
                saleTypeBoxLabel.innerText = "Chọn loại Kho Sale";
            } else {
                saleTypeBoxLabel.innerText = "Chọn loại hủy từ Kho Sale";
            }
        }

    } else {
        saleTypeBox.classList.add("d-none");
        resetQuickCheckSaleType();
    }
    });
});

if (quickCheckProductInput) {
    quickCheckProductInput.addEventListener("change", function () {
        const selectedProduct = findQuickCheckSelectedProduct();

        if (selectedProduct) {
            quickCheckProductInput.value = selectedProduct.name;
            quickCheckProductCodeInput.value = selectedProduct.code;
            quickCheckUnitInput.value = selectedProduct.unit || "cành";
        } else {
            quickCheckProductCodeInput.value = "";
            quickCheckUnitInput.value = "cành";
        }

        quickCheckCurrentStockInput.value = "0";
    });
}

function addQuickCheckItem() {
    if (!quickCheckProductInput || !quickCheckQuantityInput) return;

    const selectedWarehouse = document.querySelector('input[name="check_warehouse_type"]:checked')?.value || "";
    const productGroup = document.querySelector('input[name="check_product_group"]:checked')?.value || "";
    const saleType = document.querySelector('input[name="check_sale_type"]:checked')?.value || "";

    let selectedProduct = findQuickCheckSelectedProduct();

    const inputValue = quickCheckProductInput.value.trim();

    let productCode = "";
    let productName = inputValue;
    let unit = quickCheckUnitInput ? quickCheckUnitInput.value.trim() : "cành";

    if (selectedProduct) {
        productCode = selectedProduct.code || "";
        productName = selectedProduct.name || inputValue;
        unit = selectedProduct.unit || unit || "cành";
    } else {
        productCode = quickCheckProductCodeInput ? quickCheckProductCodeInput.value.trim() : "";
    }

    const currentStock = Number(quickCheckCurrentStockInput ? quickCheckCurrentStockInput.value || 0 : 0);
    const quantity = Number(quickCheckQuantityInput.value || 0);

    if (!productGroup) {
        alert("Vui lòng chọn nhóm hàng kiểm kê.");
        return;
    }

    if (!selectedWarehouse) {
        alert("Vui lòng chọn kho nhận dữ liệu sau kiểm kê.");
        return;
    }

    if ((selectedWarehouse === "SALE" || selectedWarehouse === "DAMAGED") && !saleType) {
        alert("Vui lòng chọn loại 50c hoặc 100c.");
        return;
    }

    if (!productName) {
        alert("Vui lòng chọn hoặc nhập tên hoa/sản phẩm.");
        return;
    }

    if (quantity <= 0) {
        alert("Vui lòng nhập số lượng tồn cuối cùng lớn hơn 0.");
        return;
    }

    const cleanCode = (productCode || productName).trim().toUpperCase();
    const cleanWarehouse = selectedWarehouse.trim().toUpperCase();
    const cleanGroup = productGroup.trim().toUpperCase();
    const cleanSaleType = (saleType || "").trim().toLowerCase();

    const existedIndex = quickCheckItems.findIndex(item => {
        const itemCode = (item.product_code || item.product_name || "").trim().toUpperCase();
        const itemWarehouse = (item.warehouse_type || "").trim().toUpperCase();
        const itemGroup = (item.product_group || "").trim().toUpperCase();
        const itemSaleType = (item.sale_type || "").trim().toLowerCase();

        return (
            itemCode === cleanCode &&
            itemWarehouse === cleanWarehouse &&
            itemGroup === cleanGroup &&
            itemSaleType === cleanSaleType
        );
    });

    const newItem = {
        product_code: productCode,
        product_name: productName,
        unit: unit || "cành",
        current_stock: currentStock,
        quantity: quantity,
        warehouse_type: selectedWarehouse,
        product_group: productGroup,
        sale_type: saleType
    };

    if (existedIndex >= 0) {
        quickCheckItems[existedIndex].quantity =
            Number(quickCheckItems[existedIndex].quantity || 0) + quantity;

        quickCheckItems[existedIndex].current_stock = currentStock;
    } else {
        quickCheckItems.push(newItem);
    }

    renderQuickCheckItems();
    resetQuickCheckProductFields();
}

function renderQuickCheckItems() {
    if (!quickCheckItemsTable || !quickCheckItemsJson) return;

    quickCheckItemsJson.value = JSON.stringify(quickCheckItems);

    if (quickCheckItemCountText) {
        quickCheckItemCountText.innerText = `${quickCheckItems.length} sản phẩm`;
    }

    if (quickCheckItems.length === 0) {
        quickCheckItemsTable.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    Chưa có sản phẩm nào
                </td>
            </tr>
        `;
        return;
    }

    quickCheckItemsTable.innerHTML = "";

    quickCheckItems.forEach(function (item, index) {
        const saleLabel = item.warehouse_type === "SALE" && item.sale_type
            ? ` / ${item.sale_type}`
            : "";

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.product_code || "-"}</td>
            <td class="fw-semibold">${item.product_name}</td>
            <td>${item.unit || "cành"}</td>
            <td>${item.warehouse_type}${saleLabel}</td>
            <td class="text-end">${item.current_stock || 0}</td>
            <td class="text-end fw-bold text-success">${item.quantity}</td>
            <td class="text-center">
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeQuickCheckItem(${index})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        quickCheckItemsTable.appendChild(row);
    });
}

function removeQuickCheckItem(index) {
    if (!confirm("Bạn có chắc muốn xóa sản phẩm này khỏi danh sách kiểm kê?")) return;

    quickCheckItems.splice(index, 1);
    renderQuickCheckItems();
}

if (quickInventoryModal) {
    quickInventoryModal.addEventListener("hidden.bs.modal", function () {
        quickCheckItems = [];
        renderQuickCheckItems();
        resetQuickCheckProductFields();
        resetQuickCheckSaleType();

        if (saleTypeBox) {
            saleTypeBox.classList.add("d-none");
        }
    });
}

const quickInventoryForm = quickInventoryModal
    ? quickInventoryModal.querySelector("form")
    : null;

if (quickInventoryForm) {
    quickInventoryForm.addEventListener("submit", function (e) {
        if (quickCheckItems.length === 0) {
            e.preventDefault();
            alert("Vui lòng thêm ít nhất một sản phẩm kiểm kê.");
            return;
        }

        quickCheckItemsJson.value = JSON.stringify(quickCheckItems);
    });
}