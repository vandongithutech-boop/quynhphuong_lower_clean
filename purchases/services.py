from django.db import transaction
from django.utils import timezone

from inventory.models import (
    InventoryReceipt,
    InventoryReceiptItem,
    InventoryStock,
    InventoryTransaction,
)

from traceability.services import (
    create_trace_lot_from_receipt_item,
    create_trace_bundles_from_purchase_item,
)


@transaction.atomic
def receive_purchase_order_to_stock(purchase_order, request=None):
    if purchase_order.status == "received":
        raise Exception("Đơn đặt mua này đã được nhập kho trước đó.")

    receipt_code = f"NK{timezone.now().strftime('%Y%m%d%H%M%S')}"

    receipt = InventoryReceipt.objects.create(
        receipt_code=receipt_code,
        product_group="HH",
        supplier_code=purchase_order.supplier_code or "",
        supplier_name=purchase_order.supplier_name,
    )

    for po_item in purchase_order.items.all():
        received_quantity = float(po_item.received_quantity or po_item.ordered_quantity or 0)

        if received_quantity <= 0:
            continue

        receipt_item = InventoryReceiptItem.objects.create(
            receipt=receipt,
            product_code=po_item.product_code,
            product_name=po_item.product_name,
            unit=po_item.unit or "cành",
            flower_grade="",
            quantity=received_quantity,
        )

        lot = create_trace_lot_from_receipt_item(
            receipt,
            receipt_item,
            request=request,
        )

        InventoryStock.objects.create(
            lot=lot,
            warehouse_type="RAW",
            product_group="HH",
            product_code=po_item.product_code,
            product_name=po_item.product_name,
            unit=po_item.unit or "cành",
            flower_grade="",
            supplier_code=purchase_order.supplier_code or "",
            supplier_name=purchase_order.supplier_name,
            received_date=timezone.now(),
            quantity=received_quantity,
        )

        InventoryTransaction.objects.create(
            lot=lot,
            transaction_code=f"GD{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
            transaction_type="IN",
            warehouse_type="RAW",
            product_group="HH",
            product_code=po_item.product_code,
            product_name=po_item.product_name,
            unit=po_item.unit or "cành",
            flower_grade="",
            supplier_code=purchase_order.supplier_code or "",
            supplier_name=purchase_order.supplier_name,
            received_date=timezone.now(),
            quantity=received_quantity,
            reference_code=receipt.receipt_code,
            note=f"Nhập kho từ đơn đặt mua {purchase_order.po_code}",
        )

        create_trace_bundles_from_purchase_item(
            lot=lot,
            product_code=po_item.product_code,
            product_name=po_item.product_name,
            supplier_code=purchase_order.supplier_code or "",
            supplier_name=purchase_order.supplier_name,
            quantity=received_quantity,
            stems_per_bundle=po_item.stems_per_bundle,
        )

    purchase_order.status = "received"
    purchase_order.received_date = timezone.localdate()
    purchase_order.save(update_fields=["status", "received_date"])

    return receipt

@transaction.atomic
def receive_purchase_pickup_to_stock(pickup, request=None):
    if pickup.status == "received":
        raise Exception("Chuyến lấy hàng này đã được nhập kho trước đó.")

    if not pickup.items.exists():
        raise Exception("Chuyến lấy hàng chưa có sản phẩm.")

    purchase_order = pickup.purchase_order

    receipt_code = f"NK{timezone.now().strftime('%Y%m%d%H%M%S')}"

    receipt = InventoryReceipt.objects.create(
        receipt_code=receipt_code,
        product_group="HH",
        supplier_code=purchase_order.supplier_code or "",
        supplier_name=purchase_order.supplier_name,
    )

    for pickup_item in pickup.items.all():
        received_quantity = float(
            pickup_item.received_quantity or pickup_item.planned_quantity or 0
        )

        if received_quantity <= 0:
            continue

        receipt_item = InventoryReceiptItem.objects.create(
            receipt=receipt,
            product_code=pickup_item.product_code,
            product_name=pickup_item.product_name,
            unit=pickup_item.unit or "cành",
            flower_grade="",
            quantity=received_quantity,
        )

        lot = create_trace_lot_from_receipt_item(
            receipt,
            receipt_item,
            request=request,
        )

        InventoryStock.objects.create(
            lot=lot,
            warehouse_type="RAW",
            product_group="HH",
            product_code=pickup_item.product_code,
            product_name=pickup_item.product_name,
            unit=pickup_item.unit or "cành",
            flower_grade="",
            supplier_code=purchase_order.supplier_code or "",
            supplier_name=purchase_order.supplier_name,
            received_date=timezone.now(),
            quantity=received_quantity,
        )

        InventoryTransaction.objects.create(
            lot=lot,
            transaction_code=f"GD{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
            transaction_type="IN",
            warehouse_type="RAW",
            product_group="HH",
            product_code=pickup_item.product_code,
            product_name=pickup_item.product_name,
            unit=pickup_item.unit or "cành",
            flower_grade="",
            supplier_code=purchase_order.supplier_code or "",
            supplier_name=purchase_order.supplier_name,
            received_date=timezone.now(),
            quantity=received_quantity,
            reference_code=receipt.receipt_code,
            note=f"Nhập kho từ chuyến lấy hàng {pickup.pickup_code} - PO {purchase_order.po_code}",
        )

        create_trace_bundles_from_purchase_item(
            lot=lot,
            product_code=pickup_item.product_code,
            product_name=pickup_item.product_name,
            supplier_code=purchase_order.supplier_code or "",
            supplier_name=purchase_order.supplier_name,
            quantity=received_quantity,
            stems_per_bundle=pickup_item.stems_per_bundle,
        )

    pickup.status = "received"
    pickup.received_date = timezone.localdate()
    pickup.save(update_fields=["status", "received_date"])

    # Cập nhật PO: nếu tất cả pickup đã received thì PO completed/received
    if not purchase_order.pickups.exclude(status="received").exists():
        purchase_order.status = "received"
        purchase_order.received_date = timezone.localdate()
        purchase_order.save(update_fields=["status", "received_date"])

    return receipt