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
    const csrftoken = getCookie("csrftoken");

    document.querySelectorAll(".driver-confirm-checkbox").forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            const row = this.closest("tr");
            const itemId = this.dataset.itemId;
            const url = this.dataset.url;

            const quantityInput = document.querySelector(
                `.driver-received-input[data-item-id="${itemId}"]`
            );

            const driverReceivedQuantity = quantityInput ? quantityInput.value : 0;
            const checked = this.checked;

            if (window.location.pathname.startsWith("/transport/")) {
                    setTimeout(function () {
                        window.location.reload();
                    }, 1500);
                }

            if (checked) {
                row.classList.add("driver-item-confirmed");
            } else {
                row.classList.remove("driver-item-confirmed");
            }

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({
                    driver_received_quantity: driverReceivedQuantity,
                    driver_confirmed: checked,
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.message || "Không lưu được dữ liệu.");
                }
            })
            .catch(error => {
                alert(error.message);

                this.checked = !checked;

                if (checked) {
                    row.classList.remove("driver-item-confirmed");
                } else {
                    row.classList.add("driver-item-confirmed");
                }
            });
        });
    });
});

function updateCompleteButtons() {
    document.querySelectorAll(".complete-po-form").forEach(function (form) {
        const poId = form.dataset.poId;

        const checkboxes = document.querySelectorAll(
            `.driver-confirm-checkbox[data-po-id="${poId}"]`
        );

        if (!checkboxes.length) {
            form.classList.add("d-none");
            return;
        }

        const allChecked = Array.from(checkboxes).every(function (checkbox) {
            return checkbox.checked;
        });

        if (allChecked) {
            form.classList.remove("d-none");
        } else {
            form.classList.add("d-none");
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    updateCompleteButtons();

    document.querySelectorAll(".driver-confirm-checkbox").forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            updateCompleteButtons();
        });
    });
});