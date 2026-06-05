from django.utils import timezone
from .models import TraceLot, TraceLog, TraceBundle

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


def generate_lot_code():
    today = timezone.localdate()
    prefix = today.strftime("LH-%d%m%y")

    last_lot = (
        TraceLot.objects
        .filter(lot_code__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_lot:
        try:
            last_number = int(last_lot.lot_code.split("-")[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    next_number = last_number + 1

    return f"{prefix}-{next_number:04d}"


def create_trace_lot_from_receipt_item(receipt, item, request=None):
    receipt_datetime = getattr(receipt, "receipt_datetime", None)

    if receipt_datetime:
        local_dt = timezone.localtime(receipt_datetime)
        received_date = local_dt.date()
        received_time = local_dt.time()
    else:
        received_date = timezone.localdate()
        received_time = timezone.localtime().time()

    lot = TraceLot.objects.create(
        lot_code=generate_lot_code(),

        product_code=item.product_code,
        product_name=item.product_name,
        unit=item.unit,

        supplier_code=getattr(receipt, "supplier_code", None),
        supplier_name=getattr(receipt, "supplier_name", None),

        received_date=received_date,
        received_time=received_time,

        received_quantity=int(item.quantity or 0),

        delivery_type="other",
        note=f"Tạo tự động từ phiếu nhập kho {getattr(receipt, 'receipt_code', '')}",
    )

    item.lot = lot
    item.save(update_fields=["lot"])

    TraceLog.objects.create(
        lot=lot,
        action="import_raw",
        from_area="Bên ngoài",
        to_area="Kho nguyên liệu",
        quantity=int(item.quantity or 0),
        employee_name=None,
        related_code=getattr(receipt, "receipt_code", None),
        note="Tự động ghi nhận khi nhập kho",
    )

    # Không tạo QR cho lô.
    # QR chỉ tạo cho từng bó TraceBundle.

    return lot


def add_trace_log(
    lot,
    action,
    quantity=0,
    from_area=None,
    to_area=None,
    employee_name=None,
    related_code=None,
    note=None,
):
    return TraceLog.objects.create(
        lot=lot,
        action=action,
        quantity=quantity or 0,
        from_area=from_area,
        to_area=to_area,
        employee_name=employee_name,
        related_code=related_code,
        note=note,
    )


def generate_qr_for_bundle(bundle, request=None):
    if request:
        trace_url = request.build_absolute_uri(f"/trace/bundle/{bundle.bundle_code}/")
    else:
        trace_url = f"/trace/bundle/{bundle.bundle_code}/"

    qr = qrcode.make(trace_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    file_name = f"{bundle.bundle_code}.png"

    bundle.qr_image.save(
        file_name,
        ContentFile(buffer.getvalue()),
        save=True
    )

    return bundle.qr_image


def create_trace_bundles_from_purchase_item(
    lot,
    product_code,
    product_name,
    supplier_code,
    supplier_name,
    quantity,
    stems_per_bundle,
    request=None,
):
    if not stems_per_bundle:
        stems_per_bundle = 50

    total_quantity = int(quantity or 0)

    bundle_count = (
        total_quantity + stems_per_bundle - 1
    ) // stems_per_bundle

    bundles = []

    for index in range(1, bundle_count + 1):

        if index < bundle_count:
            actual_stems = stems_per_bundle
        else:
            used_before = stems_per_bundle * (bundle_count - 1)
            actual_stems = total_quantity - used_before

            if actual_stems <= 0:
                actual_stems = stems_per_bundle

        bundle_code = (
            f"{lot.lot_code}-"
            f"{product_code}-"
            f"B{index:03d}"
        )

        bundle = TraceBundle.objects.create(
            bundle_code=bundle_code,

            lot=lot,

            product_code=product_code,
            product_name=product_name,

            supplier_code=supplier_code,
            supplier_name=supplier_name,

            bundle_number=index,

            expected_stems=stems_per_bundle,
            actual_stems=actual_stems,
            initial_stems=actual_stems,
            remaining_stems=actual_stems,

            source_type="purchase",
            status="raw",
        )

        generate_qr_for_bundle(bundle, request=request)

        bundles.append(bundle)

    return bundles