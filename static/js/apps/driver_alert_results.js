document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("driverAlertResultModal");
    const bodyEl = document.getElementById("driverAlertResultBody");

    if (!modalEl || !bodyEl) return;

    const resultModal = new bootstrap.Modal(modalEl);
    const seenKey = "driver_alert_results_seen";
    let seenIds = JSON.parse(localStorage.getItem(seenKey) || "[]");
    let modalShowing = false;

    function saveSeen() {
        localStorage.setItem(seenKey, JSON.stringify(seenIds));
    }

    function loadDriverResults() {
        if (modalShowing) return;

        fetch("/transport/driver/alert-results/")
            .then(res => res.json())
            .then(data => {
                if (!data.success || !data.alerts.length) return;

                const unseen = data.alerts.filter(alert => !seenIds.includes(alert.id));

                if (!unseen.length) return;

                bodyEl.innerHTML = unseen.map(alert => {
                    const isApproved = alert.status === "approved";

                    return `
                        <div class="border rounded-4 p-3 mb-3">
                            <div class="fw-bold mb-2">${alert.po_code}</div>

                            <div>Sản phẩm: <strong>${alert.product_name}</strong></div>
                            <div>SL đặt: <strong>${alert.ordered_quantity}</strong></div>
                            <div>SL bạn báo nhận:
                                <strong class="text-danger">${alert.driver_received_quantity}</strong>
                            </div>

                            <div class="mt-2">
                                ${
                                    isApproved
                                    ? `<span class="badge bg-success">Đã được duyệt nhận vượt mức</span>
                                       <div class="mt-2">Số lượng được nhận: <strong>${alert.approved_quantity}</strong></div>`
                                    : `<span class="badge bg-warning text-dark">Đã được điều chỉnh</span>
                                       <div class="mt-2">Số lượng được phép nhận: <strong>${alert.approved_quantity}</strong></div>`
                                }
                            </div>

                            <div class="text-muted small mt-2">
                                Thời gian phản hồi: ${alert.resolved_at}
                            </div>
                        </div>
                    `;
                }).join("");

                unseen.forEach(alert => seenIds.push(alert.id));
                saveSeen();

                resultModal.show();
                modalShowing = true;
            });
    }

    modalEl.addEventListener("hidden.bs.modal", function () {
        modalShowing = false;
    });

    loadDriverResults();
    setInterval(loadDriverResults, 5000);
});