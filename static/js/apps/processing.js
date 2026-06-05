let productIndex = 0;
let currentBunchItem = null;
let currentDamagedItem = null;
let startTime = null;
let timerInterval = null;
let activeRowIndex = null; 

function handleEmployeeChange(selectElement) {
    const selected = selectElement.options[selectElement.selectedIndex];

    if (!selectElement.value) {
        document.getElementById('productSection').classList.add('d-none');
        document.getElementById('employeeInfoBox').classList.add('d-none');
        document.getElementById('workingTimeDisplay').value = 'Chưa bắt đầu';
        return;
    }

    const code = selected.dataset.code;
    const name = selected.dataset.name;
    const position = selected.dataset.position;

    document.getElementById('employeeCode').value = code;
    document.getElementById('employeeName').value = name;
    document.getElementById('employeePosition').value = position;

    document.getElementById('infoEmployeeCode').innerText = code;
    document.getElementById('infoEmployeeName').innerText = name;
    document.getElementById('infoEmployeePosition').innerText = position;

    document.getElementById('employeeInfoBox').classList.remove('d-none');
    document.getElementById('productSection').classList.remove('d-none');

    if (timerInterval) clearInterval(timerInterval);

    startTime = new Date();

    const localStartTime =
        startTime.getFullYear() + '-' +
        String(startTime.getMonth() + 1).padStart(2, '0') + '-' +
        String(startTime.getDate()).padStart(2, '0') + ' ' +
        String(startTime.getHours()).padStart(2, '0') + ':' +
        String(startTime.getMinutes()).padStart(2, '0') + ':' +
        String(startTime.getSeconds()).padStart(2, '0');

    document.getElementById('startTime').value = localStartTime;
    document.getElementById('processingStartDisplay').innerText = localStartTime;

    updateWorkingTime();
    timerInterval = setInterval(updateWorkingTime, 1000);

    if (document.querySelectorAll('.product-item').length === 0) {
        addProductItem();
    }
}

function updateWorkingTime() {
    if (!startTime) return;

    const now = new Date();
    const diff = Math.floor((now - startTime) / 1000);

    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    const seconds = diff % 60;

    document.getElementById('workingTimeDisplay').value =
        `${hours} giờ ${minutes} phút ${seconds} giây`;
}

function getItemData(item) {
    const productSelect = item.querySelector('.product-select');
    if (!productSelect || !productSelect.value) return null;

    const selected = productSelect.options[productSelect.selectedIndex];
    
    let mergeSources = [];
    try {
        mergeSources = JSON.parse(item.querySelector('.merge-sources-json').value || '[]');
    } catch(e) {
        mergeSources = [];
    }

    return {
        raw_stock_id: productSelect.value,
        product_code: selected.dataset.code || '',
        product_name: selected.dataset.name || '',
        supplier_name: item.querySelector('.supplier-name').value || '',
        stock_quantity: Number(item.querySelector('.stock-quantity').value || 0),
        import_date: item.querySelector('.import-date').value || '',
        soaking_days: parseInt(item.querySelector('.soaking-days').value || 0),
        received_quantity: Number(item.querySelector('.received-quantity').value || 0),
        bunch_type: item.querySelector('.bunch-type').value || '',
        stems_per_bunch: Number(item.querySelector('.stems-per-bunch').value || 0),
        processed_stems: Number(item.querySelector('.processed-stems').value || 0),
        damaged_stems: Number(item.querySelector('.damaged-stems').value || 0),
        odd_stems: Number(item.querySelector('.odd-stems').value || 0),
        compensate_stems: Number(item.querySelector('.compensate-stems')?.value || 0),
        extra_stems: Number(item.querySelector('.extra-stems').value || 0),
        final_stems: Number(item.querySelector('.final-stems').value || 0),
        final_bunches: Number(item.querySelector('.final-bunches').value || 0),
        merge_sources: mergeSources
    };
}

function addProductItem() {
    document.querySelectorAll('.product-item').forEach(oldItem => {
        if (oldItem.dataset.finished === "1") return;

        const productSelect = oldItem.querySelector('.product-select');
        if (!productSelect || !productSelect.value) return;

        const selected = productSelect.options[productSelect.selectedIndex];
        oldItem.classList.add('processing-finished');

        const summaryHtml = `
            <div class="processing-bill-card mb-3">
                <div class="processing-bill-header">
                    <div>
                        <div class="processing-bill-title">${selected.dataset.name || 'Sản phẩm'}</div>
                        <div class="processing-bill-sub">
                            ${selected.dataset.code || ''} • ${oldItem.querySelector('.supplier-name').value || 'Chưa có NCC'}
                        </div>
                    </div>
                    <span class="badge bg-light text-success fs-6">
                        ${oldItem.querySelector('.final-bunches').value || 0} bó
                    </span>
                </div>
                <div class="processing-bill-body">
                    <div class="processing-grid">
                        <div class="processing-info"><div class="processing-label">Đã nhận</div><div class="processing-value">${oldItem.querySelector('.received-quantity').value || 0}</div></div>
                        <div class="processing-info"><div class="processing-label">Cành sơ chế</div><div class="processing-value">${oldItem.querySelector('.processed-stems').value || 0}</div></div>
                        <div class="processing-info processing-result"><div class="processing-label">Tổng cành TP</div><div class="processing-value text-success">${oldItem.querySelector('.final-stems').value || 0}</div></div>
                        <div class="processing-info"><div class="processing-label">Cành xả/hủy</div><div class="processing-value">${oldItem.querySelector('.damaged-stems').value || 0}</div></div>
                        <div class="processing-info"><div class="processing-label">Cành lẻ</div><div class="processing-value">${oldItem.querySelector('.odd-stems').value || 0}</div></div>
                        <div class="processing-info"><div class="processing-label">Quy cách bó</div><div class="processing-value">${oldItem.querySelector('.bunch-type').value || 'Chưa chọn'}</div></div>
                        <div class="processing-info processing-result"><div class="processing-label">Số bó TP</div><div class="processing-value text-success">${oldItem.querySelector('.final-bunches').value || 0}</div></div>
                    </div>
                </div>
            </div>
        `;

        const itemData = getItemData(oldItem);
        oldItem.dataset.itemJson = JSON.stringify(itemData);
        oldItem.innerHTML = summaryHtml;
        oldItem.dataset.finished = "1";
    });

    productIndex++;

    const html = `
        <div class="card border-0 shadow-sm rounded-4 mb-3 product-item processing-product-form"
            data-index="${productIndex}"
            data-odd-asked="0"
            data-finished="0">
            <div class="card-header bg-white rounded-top-4 d-flex justify-content-between align-items-center">
                <div class="fw-bold text-success">
                    <i class="bi bi-pencil-square me-2"></i>Nhập sản phẩm sơ chế #${productIndex}
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeProductItem(this)"><i class="bi bi-trash"></i></button>
            </div>
            <div class="card-body">
                ${getProductFormHtml(productIndex)}
            </div>
        </div>
    `;

    document.getElementById('productItems').insertAdjacentHTML('beforeend', html);
}

function removeProductItem(button) {
    button.closest('.product-item').remove();
}

function selectProduct(select) {
    const item = select.closest('.product-item');
    const selected = select.options[select.selectedIndex];

    if (!select.value) return;

    item.querySelector('.stock-quantity').value = selected.dataset.stock || 0;
    item.querySelector('.import-date').value = selected.dataset.importDate || 'Chưa có dữ liệu';
    item.querySelector('.supplier-name').value = selected.dataset.supplier || 'Chưa có dữ liệu';

    const importDate = selected.dataset.importDate || '';
    if (importDate) {
        const today = new Date();
        const imported = new Date(importDate);
        const diffDays = Math.floor((today - imported) / (1000 * 60 * 60 * 24));
        item.querySelector('.soaking-days').value = diffDays + ' ngày';
    } else {
        item.querySelector('.soaking-days').value = 'Chưa có dữ liệu';
    }
}

function openBunchAfterReceived(input) {
    const item = input.closest('.product-item');
    const received = Number(input.value || 0);
    const stock = Number(item.querySelector('.stock-quantity').value || 0);

    if (received <= 0) return;

    if (stock > 0 && received > stock) {
        alert('Số lượng nhận không được lớn hơn tồn kho hiện tại.');
        input.value = '';
        return;
    }

    currentBunchItem = item;

    openAppChoicePopup({
        title: 'Chọn số lượng cành/bó',
        subtitle: 'Chọn quy cách bó cho sản phẩm đang sơ chế',
        icon: '<i class="bi bi-flower1"></i>',
        choices: [
            { label: '100C', value: 100 },
            { label: '50C', value: 50 },
            { label: '40C', value: 40 },
            { label: '30C', value: 30 },
            { label: '20C', value: 20 },
            { label: 'LẺ', value: 0, className: 'secondary' },
        ],
        onSelect: function(value, label) {
            const stems = Number(value);
            if (stems === 0) {
                currentBunchItem.querySelector('.bunch-type').value = 'LẺ';
                currentBunchItem.querySelector('.stems-per-bunch').value = 0;
            } else {
                currentBunchItem.querySelector('.bunch-type').value = label + '/bó';
                currentBunchItem.querySelector('.stems-per-bunch').value = stems;
            }
            // Reset trạng thái hỏi cành lẻ nếu người dùng đổi quy cách bó
            currentBunchItem.dataset.oddAsked = "0";
            calculateItem(currentBunchItem);
        }
    });
}

function handleProcessedStemsBlur(input) {
    const item = input.closest('.product-item');
    calculateItem(item);
}

function calculateItem(item) {
    const received = Number(item.querySelector('.received-quantity').value || 0);
    const processed = Number(item.querySelector('.processed-stems').value || 0);
    const bunchSize = Number(item.querySelector('.stems-per-bunch').value || 0);
    const mergeBtn = item.querySelector('.btn-trigger-merge');

    let damaged = received - processed;
    if (damaged < 0) damaged = 0;

    let odd = 0;
    let baseBunches = 0;

    if (bunchSize > 0 && processed > 0) {
        baseBunches = Math.floor(processed / bunchSize);
        odd = processed % bunchSize;
    } else {
        odd = processed;
        baseBunches = 0;
    }

    let totalMergedStems = 0;

    try {
        const currentSources = JSON.parse(item.querySelector('.merge-sources-json').value || '[]');
        totalMergedStems = currentSources.reduce((sum, src) => sum + Number(src.quantity_used || 0), 0);
    } catch (e) {
        totalMergedStems = 0;
    }

    const compensate = Number(item.querySelector('.compensate-stems')?.value || 0);
    const totalOddCombined = odd + totalMergedStems + compensate;

    let addedBunches = 0;
    let remainingOdd = odd;

    if (bunchSize > 0 && totalOddCombined >= bunchSize) {
        addedBunches = Math.floor(totalOddCombined / bunchSize);
        remainingOdd = totalOddCombined % bunchSize;
    }

        const finalBunches = baseBunches + addedBunches;
        const finalStems = finalBunches * bunchSize;

        item.querySelector('.damaged-stems').value = damaged;
        item.querySelector('.odd-stems').value = remainingOdd;
        item.querySelector('.extra-stems').value = 0;
        item.querySelector('.final-bunches').value = finalBunches;
        item.querySelector('.final-stems').value = finalStems;

    if (mergeBtn) {
        if (bunchSize > 0 && odd > 0 && totalOddCombined < bunchSize) {
            const needed = bunchSize - totalOddCombined;
            mergeBtn.classList.remove('d-none');
            mergeBtn.innerHTML = `<i class="bi bi-patch-plus"></i> Ghép thêm ${needed}`;
        } else {
            mergeBtn.classList.add('d-none');
        }
    }
}

// BƯỚC 3: Mở Modal bù cành, tính toán đúng số cành đang thiếu
function triggerOpenLooseStemModal(button) {
    const item = button.closest('.product-item');
    const productSelect = item.querySelector('.product-select');
    if (!productSelect || !productSelect.value) {
        alert("Vui lòng chọn loại sản phẩm trước khi thực hiện bù.");
        return;
    }

    const selected = productSelect.options[productSelect.selectedIndex];
    const productCode = selected.dataset.code;
    const productName = selected.dataset.name;
    const currentSupplier = item.querySelector('.supplier-name').value;
    
    const bunchSize = Number(item.querySelector('.stems-per-bunch').value || 0);
    const odd = Number(item.querySelector('.odd-stems').value || 0);
    
    let totalMergedStems = 0;
    try {
        const currentSources = JSON.parse(item.querySelector('.merge-sources-json').value || '[]');
        totalMergedStems = currentSources.reduce((sum, src) => sum + Number(src.quantity_used || 0), 0);
    } catch(e) {}
    
    let needed = bunchSize - (odd + totalMergedStems);

    activeRowIndex = item.dataset.index;

    fetch(`/processing/api/available-loose-stems/?product_code=${productCode}`)
        .then(response => response.json())
        .then(res => {
            if (!res.success) {
                alert("Lỗi tải khay cành lẻ: " + res.error);
                return;
            }

            const tbody = document.getElementById('looseStemStockTableBody');
            tbody.innerHTML = '';

            const filteredData = res.data.filter(s => s.supplier_name !== currentSupplier);

            if (filteredData.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">Không có khay cành lẻ của nhà cung cấp khác khả dụng cho sản phẩm này.</td></tr>`;
            } else {
                filteredData.forEach(s => {
                    tbody.innerHTML += `
                        <tr data-id="${s.id}" data-supplier="${s.supplier_name}">
                            <td><span class="badge bg-secondary">${s.lot_code}</span></td>
                            <td class="fw-semibold text-dark">${s.supplier_name}</td>
                            <td>${s.employee_name} <small class="text-muted">(${s.created_at})</small></td>
                            <td class="text-end fw-bold text-warning">${s.remaining_quantity} cành</td>
                            <td>
                                <input type="number" class="form-control form-control-sm text-center qty-use-input" 
                                       min="0" max="${s.remaining_quantity}" value="0" style="font-weight: bold; color: #198754;">
                            </td>
                        </tr>
                    `;
                });
            }

            document.getElementById('looseStemModalTitle').innerHTML = 
                `<i class="bi bi-patch-plus me-2"></i>Bù hoa: ${productCode} - ${productName} <span class="ms-2 fs-6 text-warning">(Đang thiếu ${needed} cành)</span>`;
            
            const looseModal = new bootstrap.Modal(document.getElementById('looseStemMergeModal'));
            looseModal.show();
        })
        .catch(err => {
            console.error(err);
            alert("Không thể kết nối đến máy chủ.");
        });
}

// BƯỚC 4: Chốt số bù từ nhiều nguồn (Có validate tự động chống vượt hạn mức)
function applyLooseStemMerge() {
    if (!activeRowIndex) return;

    const item = document.querySelector(`.product-item[data-index="${activeRowIndex}"]`);
    const bunchSize = Number(item.querySelector('.stems-per-bunch').value || 0);
    const odd = Number(item.querySelector('.odd-stems').value || 0);
    
    const rows = document.querySelectorAll('#looseStemStockTableBody tr');
    let mergeSources = [];
    let summaryListHtml = '';
    let totalPicked = 0;

    rows.forEach(row => {
        const input = row.querySelector('.qty-use-input');
        if (input) {
            const qty = Number(input.value || 0);
            if (qty > 0) {
                const lsId = row.dataset.id;
                const supplierName = row.dataset.supplier;
                mergeSources.push({ loose_stock_id: lsId, quantity_used: qty });
                summaryListHtml += `<li><i class="bi bi-check2-circle text-success me-2"></i>Rút <strong>${qty} cành</strong> từ khay của NCC: <strong>${supplierName}</strong></li>`;
                totalPicked += qty;
            }
        }
    });

    // Validate: Ngăn chặn nhân viên chọn thừa số cành cần thiết để bù 1 bó
    let needed = bunchSize - odd;
    if (totalPicked > 0 && totalPicked > needed) {
        alert(`Bạn chỉ cần rút đúng ${needed} cành lẻ từ các khay để đủ 1 bó. Vui lòng giảm số lượng đã chọn!`);
        return; 
    }

    item.querySelector('.merge-sources-json').value = JSON.stringify(mergeSources);

    const container = item.querySelector('.merge-sources-container');
    const listUl = item.querySelector('.merge-sources-list');

    if (mergeSources.length > 0) {
        listUl.innerHTML = summaryListHtml;
        container.classList.remove('d-none');
    } else {
        listUl.innerHTML = '';
        container.classList.add('d-none');
    }

    calculateItem(item);

    const modalElement = document.getElementById('looseStemMergeModal');
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) modalInstance.hide();
    
    activeRowIndex = null;
}

document.getElementById('processingForm').addEventListener('submit', function (e) {
    const items = [];

    document.querySelectorAll('.product-item').forEach(item => {
        if (item.dataset.itemJson) {
            items.push(JSON.parse(item.dataset.itemJson));
            return;
        }

        const itemData = getItemData(item);
        if (itemData) {
            items.push(itemData);
        }
    });

    if (items.length === 0) {
        e.preventDefault();
        alert('Vui lòng thêm ít nhất một sản phẩm sơ chế.');
        return;
    }

    document.getElementById('itemsJson').value = JSON.stringify(items);
});

let manualProductIndex = 0;
let manualStartTime = null;
let manualTimerInterval = null;

function handleManualEmployeeChange(selectElement) {
    const selected = selectElement.options[selectElement.selectedIndex];

    if (!selectElement.value) {
        document.getElementById('manualProductSection').classList.add('d-none');
        document.getElementById('manualEmployeeInfoBox').classList.add('d-none');
        document.getElementById('manualWorkingTimeDisplay').value = 'Chưa bắt đầu';
        return;
    }

    const code = selected.dataset.code;
    const name = selected.dataset.name;
    const position = selected.dataset.position;

    document.getElementById('manualEmployeeCode').value = code;
    document.getElementById('manualEmployeeName').value = name;
    document.getElementById('manualEmployeePosition').value = position;

    document.getElementById('manualInfoEmployeeCode').innerText = code;
    document.getElementById('manualInfoEmployeeName').innerText = name;
    document.getElementById('manualInfoEmployeePosition').innerText = position;

    document.getElementById('manualEmployeeInfoBox').classList.remove('d-none');
    document.getElementById('manualProductSection').classList.remove('d-none');

    if (manualTimerInterval) clearInterval(manualTimerInterval);

    manualStartTime = new Date();

    const localStartTime =
        manualStartTime.getFullYear() + '-' +
        String(manualStartTime.getMonth() + 1).padStart(2, '0') + '-' +
        String(manualStartTime.getDate()).padStart(2, '0') + ' ' +
        String(manualStartTime.getHours()).padStart(2, '0') + ':' +
        String(manualStartTime.getMinutes()).padStart(2, '0') + ':' +
        String(manualStartTime.getSeconds()).padStart(2, '0');

    document.getElementById('manualStartTime').value = localStartTime;
    document.getElementById('manualProcessingStartDisplay').innerText = localStartTime;

    updateManualWorkingTime();
    manualTimerInterval = setInterval(updateManualWorkingTime, 1000);

    if (document.querySelectorAll('.manual-product-item').length === 0) {
        addManualProductItem();
    }
}

function updateManualWorkingTime() {
    if (!manualStartTime) return;

    const now = new Date();
    const diff = Math.floor((now - manualStartTime) / 1000);

    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    const seconds = diff % 60;

    document.getElementById('manualWorkingTimeDisplay').value =
        `${hours} giờ ${minutes} phút ${seconds} giây`;
}

function getManualProductFormHtml(index) {
    return `
        <div class="processing-item-row border rounded-4 p-3 bg-white mb-3 shadow-sm position-relative" data-index="${index}">
            <button type="button"
                    class="btn-close position-absolute top-0 end-0 m-3 btn-sm text-danger"
                    onclick="removeManualProductItem(this)"
                    title="Xóa dòng"></button>

            <div class="row g-3">
                <div class="manual-product-search-wrap">
                    <input type="text"
                        class="form-control form-control-sm manual-product-search"
                        placeholder="Nhập mã hoặc tên sản phẩm..."
                        autocomplete="off"
                        oninput="filterManualProductSuggest(this)"
                        onfocus="filterManualProductSuggest(this)">

                    <input type="hidden" class="manual-product-select">

                    <div class="manual-product-suggest d-none"></div>
                </div>

                <div class="col-md-2">
                    <label class="form-label fw-semibold small">Tồn kho nguyên liệu</label>
                    <input type="number" class="form-control form-control-sm manual-stock-quantity" readonly>
                </div>

                <div class="col-md-3">
                    <label class="form-label fw-semibold small">Ngày nhập gốc</label>
                    <input type="text" class="form-control form-control-sm manual-import-date" readonly>
                </div>

                <div class="col-md-2">
                    <label class="form-label fw-semibold small">Thời gian ngâm</label>
                    <input type="text" class="form-control form-control-sm manual-soaking-days" readonly>
                </div>

                <div class="col-md-4">
                    <label class="form-label fw-semibold small">Nhà cung cấp</label>
                    <input type="text" class="form-control form-control-sm manual-supplier-name" readonly>
                </div>

                <div class="col-md-2">
                    <label class="form-label fw-semibold small text-primary">Số lượng nhận *</label>
                    <input type="number"
                           class="form-control form-control-sm manual-received-quantity"
                           min="0"
                           onblur="openManualBunchAfterReceived(this)">
                </div>

                <div class="col-md-2">
                    <label class="form-label fw-semibold small">Quy cách đóng gói</label>
                    <input type="text" class="form-control form-control-sm manual-bunch-type" readonly placeholder="Chưa chọn">
                    <input type="hidden" class="manual-stems-per-bunch">
                </div>

                <div class="col-md-4">
                    <label class="form-label fw-semibold small text-primary">Số cành thực tế sơ chế *</label>
                    <input type="number"
                           class="form-control form-control-sm manual-processed-stems"
                           min="0"
                           onblur="calculateManualItem(this.closest('.manual-product-item'))">
                </div>

                <div class="col-md-2">
                    <label class="form-label fw-semibold small text-danger">Số cành xả/hủy</label>
                    <input type="number" class="form-control form-control-sm manual-damaged-stems" value="0" readonly>
                </div>

                <div class="col-md-2">
                    <label class="form-label fw-semibold small text-warning">Cành lẻ tự tính</label>
                    <input type="number" class="form-control form-control-sm manual-odd-stems" value="0" readonly>
                </div>
                <div class="col-md-2">
                    <label class="form-label fw-semibold small text-primary">Bù cành lẻ khác</label>
                    <input type="number"
                        class="form-control form-control-sm manual-compensate-stems"
                        value="0"
                        min="0"
                        oninput="calculateManualItem(this.closest('.manual-product-item'))">
                </div>
                <div class="col-md-2 d-none">
                    <label class="form-label fw-semibold small">Số cành thừa</label>
                    <input type="number" class="form-control form-control-sm manual-extra-stems" value="0" readonly>
                </div>

                <div class="col-md-3">
                    <label class="form-label fw-semibold small text-success">Tổng cành thành phẩm</label>
                    <input type="number" class="form-control form-control-sm manual-final-stems" value="0" readonly>
                </div>

                <div class="col-md-3">
                    <label class="form-label fw-semibold small text-success">Số bó thành phẩm nhập kho</label>
                    <input type="number" class="form-control form-control-sm manual-final-bunches" value="0" readonly>
                </div>
            </div>
        </div>
    `;
}

function manualRawProductOptionsHtml() {
    return window.RAW_PRODUCTS_OPTIONS_HTML || '';
}

function addManualProductItem() {
    manualProductIndex++;

    const html = `
        <div class="card border-0 shadow-sm rounded-4 mb-3 manual-product-item processing-product-form"
             data-index="${manualProductIndex}">
            <div class="card-header bg-white rounded-top-4 d-flex justify-content-between align-items-center">
                <div class="fw-bold text-success">
                    <i class="bi bi-pencil-square me-2"></i>
                    Nhập SC thủ công #${manualProductIndex}
                </div>

                <button type="button"
                        class="btn btn-sm btn-outline-danger"
                        onclick="removeManualProductItem(this)">
                    <i class="bi bi-trash"></i>
                </button>
            </div>

            <div class="card-body">
                ${getManualProductFormHtml(manualProductIndex)}
            </div>
        </div>
    `;

    document.getElementById('manualProductItems').insertAdjacentHTML('beforeend', html);
}

function removeManualProductItem(button) {
    button.closest('.manual-product-item').remove();
}

function selectManualProduct(select) {
    const item = select.closest('.manual-product-item');
    const selected = select.options[select.selectedIndex];

    if (!select.value) return;

    item.querySelector('.manual-stock-quantity').value = selected.dataset.stock || 0;
    item.querySelector('.manual-import-date').value = selected.dataset.importDate || 'Chưa có dữ liệu';
    item.querySelector('.manual-supplier-name').value = selected.dataset.supplier || 'Chưa có dữ liệu';

    const importDate = selected.dataset.importDate || '';

    if (importDate) {
        const today = new Date();
        const imported = new Date(importDate);
        const diffDays = Math.floor((today - imported) / (1000 * 60 * 60 * 24));
        item.querySelector('.manual-soaking-days').value = diffDays + ' ngày';
    } else {
        item.querySelector('.manual-soaking-days').value = 'Chưa có dữ liệu';
    }
}

function openManualBunchAfterReceived(input) {
    const item = input.closest('.manual-product-item');
    const received = Number(input.value || 0);
    const stock = Number(item.querySelector('.manual-stock-quantity').value || 0);

    if (received <= 0) return;

    if (stock > 0 && received > stock) {
        alert('Số lượng nhận không được lớn hơn tồn kho nguyên liệu hiện tại.');
        input.value = '';
        return;
    }

    openAppChoicePopup({
        title: 'Chọn số lượng cành/bó',
        subtitle: 'Chọn quy cách bó cho sản phẩm SC thủ công',
        icon: '<i class="bi bi-flower1"></i>',
        choices: [
            { label: '100C', value: 100 },
            { label: '50C', value: 50 },
            { label: '40C', value: 40 },
            { label: '30C', value: 30 },
            { label: '20C', value: 20 },
            { label: 'LẺ', value: 0, className: 'secondary' },
        ],
        onSelect: function(value, label) {
            const stems = Number(value);

            if (stems === 0) {
                item.querySelector('.manual-bunch-type').value = 'LẺ';
                item.querySelector('.manual-stems-per-bunch').value = 0;
            } else {
                item.querySelector('.manual-bunch-type').value = label + '/bó';
                item.querySelector('.manual-stems-per-bunch').value = stems;
            }

            calculateManualItem(item);
        }
    });
}

function calculateManualItem(item) {
    if (!item) return;

    const received = Number(item.querySelector('.manual-received-quantity').value || 0);
    const processed = Number(item.querySelector('.manual-processed-stems').value || 0);
    const bunchSize = Number(item.querySelector('.manual-stems-per-bunch').value || 0);
    const compensate = Number(item.querySelector('.manual-compensate-stems')?.value || 0);

    let damaged = received - processed;
    if (damaged < 0) damaged = 0;

    let odd = 0;
    let baseBunches = 0;

    if (bunchSize > 0 && processed > 0) {
        baseBunches = Math.floor(processed / bunchSize);
        odd = processed % bunchSize;
    } else {
        baseBunches = 0;
        odd = processed;
    }

    const totalOddCombined = odd + compensate;

    let addedBunches = 0;
    let remainingOdd = odd;

    if (bunchSize > 0 && totalOddCombined >= bunchSize) {
        addedBunches = Math.floor(totalOddCombined / bunchSize);
        remainingOdd = totalOddCombined % bunchSize;
    }

    const finalBunches = baseBunches + addedBunches;
    const finalStems = finalBunches * bunchSize;

    item.querySelector('.manual-damaged-stems').value = damaged;
    item.querySelector('.manual-odd-stems').value = remainingOdd;

    // Giữ nguyên logic cũ của số cành thừa
    item.querySelector('.manual-extra-stems').value = 0;

    item.querySelector('.manual-final-bunches').value = finalBunches;
    item.querySelector('.manual-final-stems').value = finalStems;
}

function getManualItemData(item) {
    const productSelect = item.querySelector('.manual-product-select');

    if (!productSelect || !productSelect.value) return null;

    return {
        raw_stock_id: productSelect.value,
        product_code: productSelect.dataset.code || '',
        product_name: productSelect.dataset.name || '',
        supplier_name: item.querySelector('.manual-supplier-name').value || '',
        stock_quantity: Number(item.querySelector('.manual-stock-quantity').value || 0),
        import_date: item.querySelector('.manual-import-date').value || '',
        soaking_days: parseInt(item.querySelector('.manual-soaking-days').value || 0),
        received_quantity: Number(item.querySelector('.manual-received-quantity').value || 0),
        bunch_type: item.querySelector('.manual-bunch-type').value || '',
        stems_per_bunch: Number(item.querySelector('.manual-stems-per-bunch').value || 0),
        processed_stems: Number(item.querySelector('.manual-processed-stems').value || 0),
        damaged_stems: Number(item.querySelector('.manual-damaged-stems').value || 0),
        odd_stems: Number(item.querySelector('.manual-odd-stems').value || 0),
        compensate_stems: Number(item.querySelector('.manual-compensate-stems')?.value || 0),
        compensate_stems: Number(item.querySelector('.manual-compensate-stems')?.value || 0),
        extra_stems: Number(item.querySelector('.manual-extra-stems').value || 0),
        final_stems: Number(item.querySelector('.manual-final-stems').value || 0),
        final_bunches: Number(item.querySelector('.manual-final-bunches').value || 0),
        merge_sources: []
    };
}

document.getElementById('manualProcessingForm')?.addEventListener('submit', function (e) {
    const items = [];

    document.querySelectorAll('.manual-product-item').forEach(item => {
        const itemData = getManualItemData(item);

        if (itemData) {
            items.push(itemData);
        }
    });

    if (items.length === 0) {
        e.preventDefault();
        alert('Vui lòng thêm ít nhất một sản phẩm SC thủ công.');
        return;
    }

    document.getElementById('manualItemsJson').value = JSON.stringify(items);
});

function getManualRawProductsData() {
    const temp = document.createElement('select');
    temp.innerHTML = window.RAW_PRODUCTS_OPTIONS_HTML || '';

    return Array.from(temp.options).map(option => ({
        id: option.value,
        code: option.dataset.code || '',
        name: option.dataset.name || '',
        stock: option.dataset.stock || 0,
        unit: option.dataset.unit || '',
        grade: option.dataset.grade || '',
        group: option.dataset.group || '',
        importDate: option.dataset.importDate || '',
        supplierCode: option.dataset.supplierCode || '',
        supplier: option.dataset.supplier || '',
        text: option.textContent.trim()
    }));
}

function filterManualProductSuggest(input) {
    const item = input.closest('.manual-product-item');
    const box = item.querySelector('.manual-product-suggest');
    const keyword = input.value.trim().toLowerCase();

    const products = getManualRawProductsData();

    const filtered = products.filter(p => {
        return (
            p.code.toLowerCase().includes(keyword) ||
            p.name.toLowerCase().includes(keyword) ||
            p.supplier.toLowerCase().includes(keyword)
        );
    }).slice(0, 20);

    if (filtered.length === 0) {
        box.innerHTML = `
            <div class="manual-suggest-empty">
                Không tìm thấy sản phẩm phù hợp
            </div>
        `;
        box.classList.remove('d-none');
        return;
    }

    box.innerHTML = filtered.map(p => `
        <button type="button"
                class="manual-suggest-item"
                onclick="chooseManualProduct(this)"
                data-id="${p.id}"
                data-code="${p.code}"
                data-name="${p.name}"
                data-stock="${p.stock}"
                data-unit="${p.unit}"
                data-grade="${p.grade}"
                data-group="${p.group}"
                data-import-date="${p.importDate}"
                data-supplier-code="${p.supplierCode}"
                data-supplier="${p.supplier}">
            <div class="fw-bold text-success">${p.code} - ${p.name}</div>
            <div class="small text-muted">
                NCC: ${p.supplier || 'Chưa có'} • Tồn: ${p.stock} ${p.unit || ''}
            </div>
        </button>
    `).join('');

    box.classList.remove('d-none');
}

function chooseManualProduct(button) {
    const item = button.closest('.manual-product-item');

    item.querySelector('.manual-product-search').value =
        `${button.dataset.code} - ${button.dataset.name}`;

    const hidden = item.querySelector('.manual-product-select');
    hidden.value = button.dataset.id;
    hidden.dataset.code = button.dataset.code || '';
    hidden.dataset.name = button.dataset.name || '';
    hidden.dataset.stock = button.dataset.stock || 0;
    hidden.dataset.unit = button.dataset.unit || '';
    hidden.dataset.grade = button.dataset.grade || '';
    hidden.dataset.group = button.dataset.group || '';
    hidden.dataset.importDate = button.dataset.importDate || '';
    hidden.dataset.supplierCode = button.dataset.supplierCode || '';
    hidden.dataset.supplier = button.dataset.supplier || '';

    item.querySelector('.manual-stock-quantity').value = button.dataset.stock || 0;
    item.querySelector('.manual-import-date').value = button.dataset.importDate || 'Chưa có dữ liệu';
    item.querySelector('.manual-supplier-name').value = button.dataset.supplier || 'Chưa có dữ liệu';

    const importDate = button.dataset.importDate || '';

    if (importDate) {
        const today = new Date();
        const imported = new Date(importDate);
        const diffDays = Math.floor((today - imported) / (1000 * 60 * 60 * 24));
        item.querySelector('.manual-soaking-days').value = diffDays + ' ngày';
    } else {
        item.querySelector('.manual-soaking-days').value = 'Chưa có dữ liệu';
    }

    item.querySelector('.manual-product-suggest').classList.add('d-none');

    document.activeElement?.blur();
}

function parseDateTimeLocal(value) {
    if (!value) return null;

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return null;
    }

    return date;
}

function calculateHoursBetween(startValue, endValue) {
    const start = parseDateTimeLocal(startValue);
    const end = parseDateTimeLocal(endValue);

    if (!start || !end) return 0;
    if (end <= start) return 0;

    const diffMs = end - start;
    return Math.round((diffMs / 1000 / 60 / 60) * 100) / 100;
}

function formatHourText(hours) {
    return `${hours.toFixed(2)} giờ`;
}

function calculateWorkTime(panel) {
    if (!panel) return;

    const shift1Start = panel.querySelector('input[name="shift1_start"]')?.value || '';
    const shift1End = panel.querySelector('input[name="shift1_end"]')?.value || '';

    const shift2Start = panel.querySelector('input[name="shift2_start"]')?.value || '';
    const shift2End = panel.querySelector('input[name="shift2_end"]')?.value || '';

    const shift1Hours = calculateHoursBetween(shift1Start, shift1End);
    const shift2Hours = calculateHoursBetween(shift2Start, shift2End);

    const totalHours = Math.round((shift1Hours + shift2Hours) * 100) / 100;
    const overtimeHours = Math.max(Math.round((totalHours - 8) * 100) / 100, 0);

    panel.querySelector('.shift1-hours-display').value = formatHourText(shift1Hours);
    panel.querySelector('.shift2-hours-display').value = formatHourText(shift2Hours);
    panel.querySelector('.total-work-hours-display').value = formatHourText(totalHours);
    panel.querySelector('.overtime-hours-display').value = formatHourText(overtimeHours);
}