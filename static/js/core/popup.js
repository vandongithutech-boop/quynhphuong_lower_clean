
    function closeAppPopup() {
        document.getElementById('appPopupOverlay').classList.remove('active');
    }

    function openAppChoicePopup(options) {
        const overlay = document.getElementById('appPopupOverlay');

        document.getElementById('appPopupTitle').innerText = options.title || 'Chọn dữ liệu';
        document.getElementById('appPopupSubtitle').innerText = options.subtitle || '';
        document.getElementById('appPopupIcon').innerHTML = options.icon || '<i class="bi bi-check2-circle"></i>';

        let bodyHtml = '<div class="app-popup-grid">';

        options.choices.forEach(choice => {
            bodyHtml += `
                <button type="button"
                        class="app-popup-choice ${choice.className || ''}"
                        data-value="${choice.value}"
                        data-label="${choice.label}">
                    ${choice.label}
                </button>
            `;
        });

        bodyHtml += '</div>';

        document.getElementById('appPopupBody').innerHTML = bodyHtml;
        document.getElementById('appPopupFooter').innerHTML = `
            <button type="button" class="app-popup-btn app-popup-btn-light" onclick="closeAppPopup()">
                Đóng
            </button>
        `;

        document.querySelectorAll('#appPopupOverlay .app-popup-choice').forEach(btn => {
            btn.onclick = function () {
                const value = this.dataset.value;
                const label = this.dataset.label;

                if (typeof options.onSelect === 'function') {
                    options.onSelect(value, label);
                }

                closeAppPopup();
            };
        });

        overlay.classList.add('active');
    }

    function openAppInputPopup(options) {
    const overlay = document.getElementById('appPopupOverlay');

    // Tạm tắt focus trap của Bootstrap modal cha nếu đang mở
    const parentModalEl = document.querySelector('.modal.show');
    let parentModalInstance = null;

    if (parentModalEl) {
        parentModalInstance = bootstrap.Modal.getInstance(parentModalEl);

        if (parentModalInstance && parentModalInstance._focustrap) {
            parentModalInstance._focustrap.deactivate();
        }
    }

    document.getElementById('appPopupTitle').innerText = options.title || 'Nhập dữ liệu';
    document.getElementById('appPopupSubtitle').innerText = options.subtitle || '';
    document.getElementById('appPopupIcon').innerHTML = options.icon || '<i class="bi bi-pencil-square"></i>';

    document.getElementById('appPopupBody').innerHTML = `
        <label class="form-label fw-semibold">${options.label || 'Giá trị'}</label>
        <input type="${options.type || 'text'}"
               class="form-control app-popup-input"
               id="appPopupInput"
               value="${options.defaultValue || ''}"
               min="${options.min || ''}"
               placeholder="${options.placeholder || ''}">
    `;

    document.getElementById('appPopupFooter').innerHTML = `
        <button type="button" class="app-popup-btn app-popup-btn-light" id="appPopupCancelBtn">
            Hủy
        </button>
        <button type="button" class="app-popup-btn app-popup-btn-success" id="appPopupConfirmBtn">
            Xác nhận
        </button>
    `;

    function closeAndRestoreFocus() {
        closeAppPopup();

        if (parentModalInstance && parentModalInstance._focustrap) {
            setTimeout(() => {
                parentModalInstance._focustrap.activate();
            }, 100);
        }
    }

    document.getElementById('appPopupCancelBtn').onclick = function () {
        closeAndRestoreFocus();
    };

    document.getElementById('appPopupConfirmBtn').onclick = function () {
        const value = document.getElementById('appPopupInput').value;

        if (typeof options.onConfirm === 'function') {
            options.onConfirm(value);
        }

        closeAndRestoreFocus();
    };

    overlay.classList.add('active');

    setTimeout(() => {
        const input = document.getElementById('appPopupInput');

        if (input) {
            input.focus();
            input.select();
        }
    }, 150);
}
