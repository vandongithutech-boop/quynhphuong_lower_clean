from django.utils import timezone
from traceability.services import add_trace_log


def generate_shipment_code():
    now = timezone.now()
    return f"XH{now.strftime('%d%m%y%H%M%S')}"


def write_trace_logs_for_shipment(shipment):
    for box in shipment.boxes.all():
        for box_item in box.items.select_related("lot").all():
            if not box_item.lot:
                continue

            add_trace_log(
                lot=box_item.lot,
                action="other",
                quantity=box_item.stems or 0,
                from_area=f"Thùng {box.box_code}",
                to_area="Xuất hàng",
                employee_name="",
                related_code=shipment.shipment_code,
                note=(
                    f"Xuất hàng {shipment.shipment_code} | "
                    f"Khách: {shipment.customer_name or '-'} | "
                    f"Container: {shipment.container_code or '-'} | "
                    f"Xe: {shipment.vehicle_info or '-'}"
                ),
            )