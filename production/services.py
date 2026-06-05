from django.db.models import Sum
from django.utils import timezone

from inventory.models import InventoryStock
from processing.models import ProcessingTicketItem
from orders.models import Order
from .models import ProductionOrder, ProductionItem
from traceability.services import add_trace_log


def generate_production_code(order):
    time_code = timezone.now().strftime("%d%m%y%H%M")
    return f"SX{time_code}-{order.id}"


def get_finished_stock(product_code="", product_name=""):
    stocks = InventoryStock.objects.filter(
        warehouse_type="FINISHED"
    )

    if product_code:
        stocks = stocks.filter(product_code=product_code)

    elif product_name:
        stocks = stocks.filter(product_name__icontains=product_name)

    return stocks.aggregate(
        total=Sum("quantity")
    )["total"] or 0


def get_raw_stock(product_code="", product_name=""):
    stocks = InventoryStock.objects.filter(warehouse_type="RAW")

    if product_code:
        stocks = stocks.filter(product_code__icontains=product_code)
    elif product_name:
        stocks = stocks.filter(product_name__icontains=product_name)

    return stocks.aggregate(total=Sum("quantity"))["total"] or 0


def create_production_from_order(order):
    production_order, created = ProductionOrder.objects.get_or_create(
        order=order,
        defaults={
            "production_code": generate_production_code(order),
            "order_code": order.order_code,
            "customer_name": order.customer_name,
            "status": "waiting",
        }
    )

    if not created:
        return production_order

    for item in order.items.all():
        standard_qty = float(item.standard_quantity or 0)
        sale_qty = float(item.sale_quantity or 0)
        required_qty = standard_qty + sale_qty
        is_sale_item = sale_qty > 0

        finished_available = get_finished_stock(
            product_code=item.product_code,
            product_name=item.product_name
        )

        missing_qty = max(required_qty - finished_available, 0)

        raw_available = 0
        need_processing_qty = 0
        warning_note = ""

        if standard_qty > 0 and missing_qty > 0:
            raw_available = get_raw_stock(
                product_code=item.product_code,
                product_name=item.product_name
            )

            need_processing_qty = min(missing_qty, raw_available)

            if raw_available > 0:
                if raw_available >= missing_qty:
                    warning_note = (
                        f"Thành phẩm thiếu {missing_qty}c. "
                        f"Kho nguyên liệu còn {raw_available}c. "
                        f"Cần sơ chế thêm {need_processing_qty}c để đủ đơn."
                    )
                else:
                    warning_note = (
                        f"Thành phẩm thiếu {missing_qty}c. "
                        f"Kho nguyên liệu chỉ còn {raw_available}c, "
                        f"vẫn thiếu {missing_qty - raw_available}c sau khi sơ chế."
                    )
            else:
                warning_note = f"Thành phẩm thiếu {missing_qty}c, kho nguyên liệu không còn hàng."

    production_item = ProductionItem.objects.create(
        production_order=production_order,
        order_item=item,
        lot=item.lot,
        product_code=item.product_code,
        product_name=item.product_name,
        flower_type=item.flower_type,
        group_name=item.group_name,
        unit=item.unit,
        standard_quantity=standard_qty,
        sale_quantity=sale_qty,
        required_quantity=required_qty,
        finished_available=finished_available,
        missing_quantity=missing_qty,
        raw_available=raw_available,
        need_processing_quantity=need_processing_qty,
        warning_note=warning_note,
        is_sale_item=is_sale_item,
    )      

    if item.lot:
        add_trace_log(
        lot=item.lot,
        action="other",
        quantity=required_qty,
        from_area="Đơn hàng",
        to_area="Sản xuất",
        employee_name="",
        related_code=production_order.production_code,
        note=f"Nhận vào sản xuất từ đơn hàng {order.order_code}",
    )   

    return production_order

def sync_production_items_from_order(production_order):
    order = production_order.order

    for order_item in order.items.all():
        exists = production_order.items.filter(order_item=order_item).exists()

        if exists:
            continue

        standard_qty = float(order_item.standard_quantity or 0)
        sale_qty = float(order_item.sale_quantity or 0)
        required_qty = standard_qty + sale_qty

        ProductionItem.objects.create(
            production_order=production_order,
            order_item=order_item,
            lot=order_item.lot,
            product_code=order_item.product_code,
            product_name=order_item.product_name,
            flower_type=order_item.flower_type,
            group_name=order_item.group_name,
            unit=order_item.unit,
            standard_quantity=standard_qty,
            sale_quantity=sale_qty,
            required_quantity=required_qty,
            is_sale_item=sale_qty > 0,
        )

        if order_item.lot:
            add_trace_log(
                lot=order_item.lot,
                action="other",
                quantity=required_qty,
                from_area="Đơn hàng",
                to_area="Sản xuất",
                employee_name="",
                related_code=production_order.production_code,
                note=f"Đồng bộ vào sản xuất từ đơn hàng {order.order_code}",
            )

    return production_order