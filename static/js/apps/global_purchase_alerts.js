function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("globalPurchaseAlertModal");
    const bodyEl = document.getElementById("globalPurchaseAlertBody");

    if (!modalEl || !bodyEl) return;

    const csrftoken = getCookie("csrftoken");
    const alertModal = new bootstrap.Modal(modalEl);

    let modalShowing = false;

    function closeModalIfEmpty() {
        if (!bodyEl.querySelector(".global-alert-item")) {
            alertModal.hide();
            modalShowing = false;
        }
    }

    function renderAlerts(alerts) {
        if (!alerts.length) {
            bodyEl.innerHTML = "";
            alertModal.hide();
            modalShowing = false;
            return;
        }

        bodyEl.innerHTML = alerts.map(alert => `
            <div class="global-alert-item border rounded-4 p-3 mb-3" data-alert-id="${alert.id}">
                <div class="fw-bold mb-2">${alert.po_code}</div>

                <div>Nhà cung cấp: <strong>${alert.supplier_name || "-"}</strong></div>
                <div>Tài xế: <strong>${alert.driver_name || "-"}</strong></div>

                <div class="mt-2">Sản phẩm: <strong>${alert.product_name}</strong></div>
                <div>SL đặt: <strong>${alert.ordered_quantity}</strong></div>
                <div>SL tài xế báo nhận:
                    <strong class="text-danger">${alert.driver_received_quantity}</strong>
                </div>

                <div class="text-muted mt-2">${alert.message || ""}</div>

                <div class="d-flex gap-2 mt-3">
                    <button class="btn btn-success btn-approve-alert" data-alert-id="${alert.id}">
                        Nhận
                    </button>

                    <button class="btn btn-outline-danger btn-open-reject" data-alert-id="${alert.id}">
                        Không nhận
                    </button>
                </div>

                <div class="reject-quantity-box mt-3 d-none" id="rejectBox${alert.id}">
                    <label class="form-label fw-bold">Số lượng được phép nhận</label>

                    <div class="d-flex gap-2">
                        <input type="number"
                               class="form-control reject-quantity-input"
                               id="rejectQty${alert.id}"
                               value="${alert.ordered_quantity}"
                               min="0"
                               step="0.01">

                        <button class="btn btn-danger btn-reject-alert" data-alert-id="${alert.id}">
                            Chấp nhận
                        </button>
                    </div>
                </div>
            </div>
        `).join("");

        alertModal.show();
        modalShowing = true;
    }

    function loadAlerts() {
        fetch("/purchases/alerts/pending/")
            .then(res => res.json())
            .then(data => {
                if (!data.success) return;

                const alerts = data.alerts || [];

                if (alerts.length === 0) {
                    bodyEl.innerHTML = "";
                    alertModal.hide();
                    modalShowing = false;
                    return;
                }

                const currentIds = alerts.map(alert => String(alert.id));

                document.querySelectorAll(".global-alert-item").forEach(function (item) {
                    const itemId = item.dataset.alertId;

                    if (!currentIds.includes(String(itemId))) {
                        item.remove();
                    }
                });

                if (modalShowing) {
                    closeModalIfEmpty();
                    return;
                }

                renderAlerts(alerts);
            })
            .catch(() => {});
    }

    bodyEl.addEventListener("click", function (event) {
        const approveBtn = event.target.closest(".btn-approve-alert");
        const openRejectBtn = event.target.closest(".btn-open-reject");
        const rejectBtn = event.target.closest(".btn-reject-alert");

        if (approveBtn) {
            const alertId = approveBtn.dataset.alertId;

            approveBtn.disabled = true;
            approveBtn.innerText = "Đang xử lý...";

            fetch(`/purchases/alerts/${alertId}/approve/`)
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const item = document.querySelector(`.global-alert-item[data-alert-id="${alertId}"]`);
                        if (item) item.remove();

                        closeModalIfEmpty();
                    }
                });

            return;
        }

        if (openRejectBtn) {
            const alertId = openRejectBtn.dataset.alertId;
            const rejectBox = document.getElementById(`rejectBox${alertId}`);

            if (rejectBox) {
                rejectBox.classList.remove("d-none");
            }

            return;
        }

        if (rejectBtn) {
            const alertId = rejectBtn.dataset.alertId;
            const qtyInput = document.getElementById(`rejectQty${alertId}`);
            const qty = qtyInput ? qtyInput.value : "";

            if (!qty) {
                alert("Vui lòng nhập số lượng được phép nhận.");
                return;
            }

            rejectBtn.disabled = true;
            rejectBtn.innerText = "Đang xử lý...";

            fetch(`/purchases/alerts/${alertId}/reject/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({
                    approved_quantity: qty,
                }),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const item = document.querySelector(`.global-alert-item[data-alert-id="${alertId}"]`);
                    if (item) item.remove();

                    closeModalIfEmpty();
                } else {
                    alert(data.message || "Không xử lý được cảnh báo.");
                    rejectBtn.disabled = false;
                    rejectBtn.innerText = "Chấp nhận";
                }
            });

            return;
        }
    });

    modalEl.addEventListener("hidden.bs.modal", function () {
        modalShowing = false;
    });

    loadAlerts();
    setInterval(loadAlerts, 3000);
});