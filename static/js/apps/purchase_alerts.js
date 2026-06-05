document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("purchaseAlertModal");
    const bodyEl = document.getElementById("purchaseAlertBody");

    if (!modalEl || !bodyEl) return;

    const alertModal = new bootstrap.Modal(modalEl);

    function loadAlerts() {
        fetch("/purchases/alerts/pending/")
            .then(res => res.json())
            .then(data => {
                if (!data.success || data.alerts.length === 0) return;

                const alert = data.alerts[0];

                bodyEl.innerHTML = `
                    <div class="border rounded-4 p-3">
                        <div class="fw-bold mb-2">${alert.po_code}</div>
                        <div>Sản phẩm: <strong>${alert.product_name}</strong></div>
                        <div>SL đặt: <strong>${alert.ordered_quantity}</strong></div>
                        <div>SL tài xế báo nhận: <strong class="text-danger">${alert.driver_received_quantity}</strong></div>
                        <div class="text-muted mt-2">${alert.message}</div>

                        <div class="d-flex gap-2 mt-4">
                            <button class="btn btn-success" onclick="resolvePurchaseAlert(${alert.id}, 'approve')">
                                Nhận
                            </button>
                            <button class="btn btn-outline-danger" onclick="resolvePurchaseAlert(${alert.id}, 'reject')">
                                Không nhận
                            </button>
                        </div>
                    </div>
                `;

                alertModal.show();
            });
    }

    window.resolvePurchaseAlert = function (alertId, action) {
        fetch(`/purchases/alerts/${alertId}/${action}/`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alertModal.hide();
                    loadAlerts();
                }
            });
    };

    setInterval(loadAlerts, 5000);
});