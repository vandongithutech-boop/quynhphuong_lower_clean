import json
from datetime import datetime

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.http import JsonResponse, request
from django.views.decorators.http import require_GET

from traceability.services import add_trace_log
from employees.models import Employee
from inventory.models import InventoryStock, InventoryTransaction

from .models import (
    ProcessingTicket,
    ProcessingTicketItem,
    LooseStemStock,
    LooseStemMerge,
    LooseStemMergeItem,
)



def get_default_business_date():
    now = timezone.localtime(timezone.now())

    # Sau 00:00 đến trước 06:00 vẫn tính cho ngày hôm trước
    if now.hour < 6:
        return now.date() - timezone.timedelta(days=1)

    return now.date()


def parse_business_date(value):
    if not value:
        return get_default_business_date()

    try:
        return timezone.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return get_default_business_date()

def generate_processing_code():
    today = timezone.now().strftime("%Y%m%d")
    prefix = f"SC{today}"

    last_ticket = (
        ProcessingTicket.objects
        .filter(ticket_code__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_ticket:
        try:
            last_number = int(last_ticket.ticket_code[-4:])
        except Exception:
            last_number = 0
    else:
        last_number = 0

    return f"{prefix}{last_number + 1:04d}"

def generate_manual_processing_code():
    today = timezone.now().strftime("%Y%m%d")
    prefix = f"SCM{today}"

    last_ticket = (
        ProcessingTicket.objects
        .filter(ticket_code__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_ticket:
        try:
            last_number = int(last_ticket.ticket_code[-4:])
        except Exception:
            last_number = 0
    else:
        last_number = 0

    return f"{prefix}{last_number + 1:04d}"

def generate_transaction_code():
    today = timezone.now().strftime("%Y%m%d")
    prefix = f"GD{today}"

    last_transaction = (
        InventoryTransaction.objects
        .filter(transaction_code__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_transaction:
        try:
            last_number = int(last_transaction.transaction_code[-4:])
        except Exception:
            last_number = 0
    else:
        last_number = 0

    return f"{prefix}{last_number + 1:04d}"


def generate_merge_code():
    today = timezone.now().strftime("%Y%m%d")
    prefix = f"GB{today}"

    last_merge = (
        LooseStemMerge.objects
        .filter(merge_code__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_merge:
        try:
            last_number = int(last_merge.merge_code[-4:])
        except Exception:
            last_number = 0
    else:
        last_number = 0

    return f"{prefix}{last_number + 1:04d}"


def parse_start_time(value):
    if not value:
        return timezone.now()

    try:
        naive_time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return timezone.make_aware(naive_time)
    except Exception:
        return timezone.now()

def parse_shift_datetime(value):
    if not value:
        return None

    try:
        naive_time = datetime.strptime(value, "%Y-%m-%dT%H:%M")
        return timezone.make_aware(naive_time)
    except Exception:
        return None


def calc_shift_hours(start, end):
    if not start or not end:
        return 0

    if end <= start:
        return 0

    return round((end - start).total_seconds() / 3600, 2)


def processing_list(request):
    employees = Employee.objects.filter(
        bo_phan__icontains="sản xuất",
        chuc_vu__icontains="sơ chế",
        trang_thai__icontains="Đang làm",
    )

    raw_products = (
        InventoryStock.objects
        .filter(
            warehouse_type="RAW",
            quantity__gt=0,
        )
        .order_by("product_name", "received_date")
    )

    tickets = ProcessingTicket.objects.all().order_by("-id")

    return render(
        request,
        "processing/processing_list.html",
        {
            "employees": employees,
            "raw_products": raw_products,
            "tickets": tickets,
            "business_date": get_default_business_date(),
        }
    )


@transaction.atomic
def create_processing_ticket(request):
    if request.method != "POST":
        return redirect("processing_list")
    business_date = parse_business_date(request.POST.get("business_date"))

    employee_code = request.POST.get("employee_code")
    employee_name = request.POST.get("employee_name")
    employee_position = request.POST.get("employee_position")
    start_time_value = request.POST.get("start_time")
    items_json = request.POST.get("items_json")

    if not employee_code or not employee_name:
        messages.error(request, "Vui lòng chọn nhân viên sơ chế.")
        return redirect("processing_list")

    if not items_json:
        messages.error(request, "Vui lòng thêm ít nhất một sản phẩm sơ chế.")
        return redirect("processing_list")

    try:
        items = json.loads(items_json)
    except Exception:
        messages.error(request, "Dữ liệu sản phẩm sơ chế không hợp lệ.")
        return redirect("processing_list")

    if not items:
        messages.error(request, "Vui lòng thêm ít nhất một sản phẩm sơ chế.")
        return redirect("processing_list")

    start_time = parse_start_time(start_time_value)
    end_time = timezone.now()
    total_hours = round((end_time - start_time).total_seconds() / 3600, 2)
    shift1_start = parse_shift_datetime(request.POST.get("shift1_start"))
    shift1_end = parse_shift_datetime(request.POST.get("shift1_end"))
    shift2_start = parse_shift_datetime(request.POST.get("shift2_start"))
    shift2_end = parse_shift_datetime(request.POST.get("shift2_end"))

    shift1_hours = calc_shift_hours(shift1_start, shift1_end)
    shift2_hours = calc_shift_hours(shift2_start, shift2_end)

    total_work_hours = round(shift1_hours + shift2_hours, 2)
    overtime_hours = round(max(total_work_hours - 8, 0), 2)

    work_note = request.POST.get("work_note", "")

    ticket = ProcessingTicket.objects.create(
        ticket_code=generate_processing_code(),
        employee_code=employee_code,
        employee_name=employee_name,
        employee_position=employee_position,
        start_time=start_time,
        end_time=end_time,
        total_hours=total_hours,
        business_date=business_date,

        shift1_start=shift1_start,
        shift1_end=shift1_end,
        shift1_hours=shift1_hours,

        shift2_start=shift2_start,
        shift2_end=shift2_end,
        shift2_hours=shift2_hours,

        total_work_hours=total_work_hours,
        overtime_hours=overtime_hours,
        work_note=work_note,
    )

    for item in items:
        raw_stock_id = item.get("raw_stock_id")

        raw_stock = (
            InventoryStock.objects
            .select_for_update()
            .filter(
                id=raw_stock_id,
                warehouse_type="RAW",
            )
            .first()
        )

        if not raw_stock:
            raise Exception("Không tìm thấy sản phẩm trong kho nguyên liệu.")

        received_quantity = float(item.get("received_quantity") or 0)
        processed_stems = float(item.get("processed_stems") or 0)
        damaged_stems = float(item.get("damaged_stems") or 0)
        odd_stems = float(item.get("odd_stems") or 0)
        extra_stems = float(item.get("extra_stems") or 0)
        final_stems = float(item.get("final_stems") or 0)
        final_bunches = float(item.get("final_bunches") or 0)
        stems_per_bunch = int(item.get("stems_per_bunch") or 0)
        merge_sources = item.get("merge_sources", [])

        if received_quantity <= 0:
            raise Exception(f"Sản phẩm {raw_stock.product_name} chưa có số lượng nhận.")

        if processed_stems <= 0:
            raise Exception(f"Sản phẩm {raw_stock.product_name} chưa có số lượng cành sơ chế.")

        if raw_stock.quantity < received_quantity:
            raise Exception(
                f"Sản phẩm {raw_stock.product_name} không đủ tồn kho. "
                f"Tồn hiện tại: {raw_stock.quantity}, số lượng nhận: {received_quantity}"
            )

        ticket_item = ProcessingTicketItem.objects.create(
            ticket=ticket,
            lot=raw_stock.lot,
            raw_stock_id=raw_stock.id,

            product_group=raw_stock.product_group,
            product_code=raw_stock.product_code,
            product_name=raw_stock.product_name,
            unit=raw_stock.unit,
            flower_grade=raw_stock.flower_grade,

            supplier_code=raw_stock.supplier_code,
            supplier_name=raw_stock.supplier_name,
            received_date=raw_stock.received_date,
            soaking_days=int(item.get("soaking_days") or 0),

            stock_quantity=float(item.get("stock_quantity") or 0),
            received_quantity=received_quantity,

            bunch_type=item.get("bunch_type", ""),
            stems_per_bunch=stems_per_bunch,

            processed_stems=processed_stems,
            damaged_stems=damaged_stems,
            odd_stems=odd_stems,
            extra_stems=extra_stems,

            final_stems=final_stems,
            final_bunches=final_bunches,
        )

        # 1. Trừ kho nguyên liệu
        raw_stock.quantity -= received_quantity
        raw_stock.save()

        InventoryTransaction.objects.create(
            transaction_code=generate_transaction_code(),
            transaction_type="OUT",
            warehouse_type="RAW",

            product_group=raw_stock.product_group,
            product_code=raw_stock.product_code,
            product_name=raw_stock.product_name,
            unit=raw_stock.unit,
            flower_grade=raw_stock.flower_grade,

            supplier_code=raw_stock.supplier_code,
            supplier_name=raw_stock.supplier_name,
            received_date=raw_stock.received_date,

            quantity=received_quantity,
            reference_code=ticket.ticket_code,
            note=f"Xuất nguyên liệu sơ chế - NV: {employee_name}",
        )

        if raw_stock.lot:
            add_trace_log(
                lot=raw_stock.lot,
                action="move_to_processing",
                quantity=received_quantity,
                from_area="Kho nguyên liệu",
                to_area="Khu sơ chế",
                employee_name=employee_name,
                related_code=ticket.ticket_code,
                note="Xuất nguyên liệu đi sơ chế",
            )

        # 2. Nhập kho thành phẩm theo CÀNH, không theo bó
        finished_stems = final_bunches * stems_per_bunch

        if finished_stems > 0:
            finished_unit = raw_stock.unit or "Cành"

            finished_stock, created = InventoryStock.objects.get_or_create(
                warehouse_type="FINISHED",
                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                flower_grade=raw_stock.flower_grade,
                supplier_code=raw_stock.supplier_code,
                received_date=raw_stock.received_date,
                defaults={
                    "product_name": raw_stock.product_name,
                    "unit": finished_unit,
                    "supplier_name": raw_stock.supplier_name,
                    "quantity": 0,
                    "lot": raw_stock.lot,
                }
            )

            finished_stock.product_name = raw_stock.product_name
            finished_stock.unit = finished_unit
            finished_stock.supplier_name = raw_stock.supplier_name
            finished_stock.quantity += finished_stems

            if not finished_stock.lot:
                finished_stock.lot = raw_stock.lot

            finished_stock.save()

            InventoryTransaction.objects.create(
                transaction_code=generate_transaction_code(),
                transaction_type="IN",
                warehouse_type="FINISHED",

                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                product_name=raw_stock.product_name,
                unit=finished_unit,
                flower_grade=raw_stock.flower_grade,

                supplier_code=raw_stock.supplier_code,
                supplier_name=raw_stock.supplier_name,
                received_date=raw_stock.received_date,

                quantity=finished_stems,
                reference_code=ticket.ticket_code,
                note=(
                    f"Nhập kho thành phẩm sau sơ chế - NV: {employee_name}. "
                    f"{final_bunches} bó x {stems_per_bunch} cành/bó = {finished_stems} cành"
                ),
            )

            if raw_stock.lot:
                add_trace_log(
                    lot=raw_stock.lot,
                    action="processing_done",
                    quantity=finished_stems,
                    from_area="Khu sơ chế",
                    to_area="Kho thành phẩm",
                    employee_name=employee_name,
                    related_code=ticket.ticket_code,
                    note=(
                        f"Nhập kho thành phẩm sau sơ chế: "
                        f"{final_bunches} bó x {stems_per_bunch} cành/bó = {finished_stems} cành"
                    ),
                )

        # 3. Lưu cành lẻ vào khay cành lẻ
        if odd_stems > 0:
            LooseStemStock.objects.create(
                lot=raw_stock.lot,
                processing_item=ticket_item,

                product_code=raw_stock.product_code,
                product_name=raw_stock.product_name,
                product_group=raw_stock.product_group,

                supplier_code=raw_stock.supplier_code,
                supplier_name=raw_stock.supplier_name,

                employee_code=employee_code,
                employee_name=employee_name,

                stems_per_bunch=stems_per_bunch,
                original_quantity=odd_stems,
                remaining_quantity=odd_stems,

                is_carried_next_day=False,
                carry_date=None,

                status="available",
            )

            if raw_stock.lot:
                add_trace_log(
                    lot=raw_stock.lot,
                    action="other",
                    quantity=odd_stems,
                    from_area="Khu sơ chế",
                    to_area="Khay cành lẻ chờ ghép",
                    employee_name=employee_name,
                    related_code=ticket.ticket_code,
                    note=f"Lưu {odd_stems} cành lẻ chờ ghép",
                )

        # 4. Nhập hoa/lá phụ hủy
        if damaged_stems > 0:
            damaged_stock, created = InventoryStock.objects.get_or_create(
                warehouse_type="DAMAGED",
                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                flower_grade=raw_stock.flower_grade,
                supplier_code=raw_stock.supplier_code,
                received_date=raw_stock.received_date,
                defaults={
                    "product_name": raw_stock.product_name,
                    "unit": raw_stock.unit,
                    "supplier_name": raw_stock.supplier_name,
                    "quantity": 0,
                    "lot": raw_stock.lot,
                }
            )

            damaged_stock.product_name = raw_stock.product_name
            damaged_stock.unit = raw_stock.unit
            damaged_stock.supplier_name = raw_stock.supplier_name
            damaged_stock.quantity += damaged_stems

            if not damaged_stock.lot:
                damaged_stock.lot = raw_stock.lot

            damaged_stock.save()

            InventoryTransaction.objects.create(
                transaction_code=generate_transaction_code(),
                transaction_type="IN",
                warehouse_type="DAMAGED",

                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                product_name=raw_stock.product_name,
                unit=raw_stock.unit,
                flower_grade=raw_stock.flower_grade,

                supplier_code=raw_stock.supplier_code,
                supplier_name=raw_stock.supplier_name,
                received_date=raw_stock.received_date,

                quantity=damaged_stems,
                reference_code=ticket.ticket_code,
                note=f"Hao hụt/xả hủy trong sơ chế - NV: {employee_name}",
            )

            if raw_stock.lot:
                add_trace_log(
                    lot=raw_stock.lot,
                    action="processing_waste",
                    quantity=damaged_stems,
                    from_area="Khu sơ chế",
                    to_area="Hoa/Lá phụ hủy",
                    employee_name=employee_name,
                    related_code=ticket.ticket_code,
                    note="Xả/hủy trong quá trình sơ chế",
                )

        # 5. Xử lý ghép cành lẻ từ NCC khác
        if merge_sources:
            total_used_stems = sum(
                float(src.get("quantity_used") or 0)
                for src in merge_sources
            )

            if total_used_stems > 0:
                merge_code = generate_merge_code()

                own_odd_stems = odd_stems
                total_merge_stems = own_odd_stems + total_used_stems

                added_bunches = 0
                added_finished_stems = 0
                remaining_odd_after_merge = own_odd_stems

                if stems_per_bunch > 0:
                    added_bunches = int(total_merge_stems // stems_per_bunch)
                    added_finished_stems = added_bunches * stems_per_bunch
                    remaining_odd_after_merge = total_merge_stems % stems_per_bunch

                # Nếu ghép đủ bó thì cộng thêm thành phẩm vào kho
                if added_finished_stems > 0:
                    finished_unit = raw_stock.unit or "Cành"

                    finished_stock, created = InventoryStock.objects.get_or_create(
                        warehouse_type="FINISHED",
                        product_group=raw_stock.product_group,
                        product_code=raw_stock.product_code,
                        flower_grade=raw_stock.flower_grade,
                        supplier_code=raw_stock.supplier_code,
                        received_date=raw_stock.received_date,
                        defaults={
                            "product_name": raw_stock.product_name,
                            "unit": finished_unit,
                            "supplier_name": raw_stock.supplier_name,
                            "quantity": 0,
                            "lot": raw_stock.lot,
                        }
                    )

                    finished_stock.product_name = raw_stock.product_name
                    finished_stock.unit = finished_unit
                    finished_stock.supplier_name = raw_stock.supplier_name
                    finished_stock.quantity += added_finished_stems

                    if not finished_stock.lot:
                        finished_stock.lot = raw_stock.lot

                    finished_stock.save()

                    InventoryTransaction.objects.create(
                        transaction_code=generate_transaction_code(),
                        transaction_type="IN",
                        warehouse_type="FINISHED",
                        product_group=raw_stock.product_group,
                        product_code=raw_stock.product_code,
                        product_name=raw_stock.product_name,
                        unit=finished_unit,
                        flower_grade=raw_stock.flower_grade,
                        supplier_code=raw_stock.supplier_code,
                        supplier_name=raw_stock.supplier_name,
                        received_date=raw_stock.received_date,
                        quantity=added_finished_stems,
                        reference_code=merge_code,
                        note=(
                            f"Ghép cành lẻ thành phẩm - NV: {employee_name}. "
                            f"{added_bunches} bó x {stems_per_bunch} cành/bó = {added_finished_stems} cành"
                        ),
                    )

                    if raw_stock.lot:
                        add_trace_log(
                            lot=raw_stock.lot,
                            action="processing_done",
                            quantity=added_finished_stems,
                            from_area="Khay cành lẻ ghép",
                            to_area="Kho thành phẩm",
                            employee_name=employee_name,
                            related_code=merge_code,
                            note=(
                                f"Ghép cành lẻ tạo thêm {added_bunches} bó "
                                f"= {added_finished_stems} cành thành phẩm"
                            ),
                        )
                merge_ticket = LooseStemMerge.objects.create(
                    merge_code=merge_code,
                    product_code=raw_stock.product_code,
                    product_name=raw_stock.product_name,
                    stems_per_bunch=stems_per_bunch,
                    total_stems=total_merge_stems,
                    total_bunches=added_bunches,
                    main_lot=raw_stock.lot,
                    created_by=employee_name,
                )

                for source in merge_sources:
                    # Sau khi ghép, cập nhật lại cành lẻ của lô chính
                    if odd_stems > 0 and added_finished_stems > 0:
                        main_loose = (
                            LooseStemStock.objects
                            .filter(
                                processing_item=ticket_item,
                                lot=raw_stock.lot,
                                product_code=raw_stock.product_code,
                                status="available",
                            )
                            .order_by("-id")
                            .first()
                        )

                        if main_loose:
                            main_loose.remaining_quantity = remaining_odd_after_merge

                            if remaining_odd_after_merge <= 0:
                                main_loose.remaining_quantity = 0
                                main_loose.status = "used"

                            main_loose.save()
                    loose_stock_id = source.get("loose_stock_id")
                    quantity_used = float(source.get("quantity_used") or 0)

                    if quantity_used <= 0:
                        continue

                    loose_item = (
                        LooseStemStock.objects
                        .select_for_update()
                        .filter(id=loose_stock_id)
                        .first()
                    )

                    if not loose_item:
                        raise Exception("Không tìm thấy dữ liệu nguồn cành lẻ để ghép.")

                    if loose_item.remaining_quantity < quantity_used:
                        raise Exception(
                            f"Khay cành lẻ của NCC {loose_item.supplier_name} không đủ cành."
                        )

                    loose_item.remaining_quantity -= quantity_used

                    if loose_item.remaining_quantity <= 0:
                        loose_item.remaining_quantity = 0
                        loose_item.status = "used"

                    loose_item.save()

                    LooseStemMergeItem.objects.create(
                        merge=merge_ticket,
                        loose_stock=loose_item,
                        lot=loose_item.lot,
                        supplier_code=loose_item.supplier_code,
                        supplier_name=loose_item.supplier_name,
                        quantity_used=quantity_used,
                    )

                    if loose_item.lot:
                        add_trace_log(
                            lot=loose_item.lot,
                            action="other",
                            quantity=quantity_used,
                            from_area="Khay cành lẻ",
                            to_area=f"Lô chính {raw_stock.lot.lot_code if raw_stock.lot else ''}",
                            employee_name=employee_name,
                            related_code=merge_code,
                            note=(
                                f"Góp {quantity_used} cành lẻ để ghép cho "
                                f"{raw_stock.product_name} - NCC {raw_stock.supplier_name}"
                            ),
                        )

                    if raw_stock.lot:
                        add_trace_log(
                            lot=raw_stock.lot,
                            action="other",
                            quantity=quantity_used,
                            from_area=f"Khay cành lẻ của {loose_item.supplier_name}",
                            to_area="Bó thành phẩm",
                            employee_name=employee_name,
                            related_code=merge_code,
                            note=(
                                f"Nhận {quantity_used} cành lẻ từ NCC "
                                f"{loose_item.supplier_name} để ghép bó"
                            ),
                        )

    messages.success(
        request,
        "Đã hoàn thành phiếu sơ chế và cập nhật kho thành phẩm."
    )
    return redirect("processing_list")


@require_GET
def get_available_loose_stems(request):
    product_code = request.GET.get("product_code")

    if not product_code:
        return JsonResponse({
            "success": False,
            "error": "Thiếu mã sản phẩm."
        }, status=400)

    stocks = (
        LooseStemStock.objects
        .filter(
            product_code=product_code,
            status="available",
            remaining_quantity__gt=0
        )
        .select_related("lot")
        .order_by("created_at")
    )

    data = []

    for stock in stocks:
        data.append({
            "id": stock.id,
            "lot_code": stock.lot.lot_code if stock.lot else "Không có mã lô",
            "supplier_name": stock.supplier_name or "Chưa rõ NCC",
            "employee_name": stock.employee_name or "Chưa rõ NV",
            "remaining_quantity": stock.remaining_quantity,
            "created_at": stock.created_at.strftime("%d/%m/%Y %H:%M"),
        })

    return JsonResponse({
        "success": True,
        "data": data
    })

@transaction.atomic
def create_manual_processing_ticket(request):
    """
    Nhập SC thủ công nhưng dùng dữ liệu thật:
    - Chọn từ kho nguyên liệu RAW
    - Trừ kho nguyên liệu
    - Cộng kho thành phẩm
    - Cộng kho hủy nếu có
    - Tạo khay cành lẻ nếu có
    - Ghi transaction và trace log
    - Lưu ngày nghiệp vụ + ca làm việc nhân viên sơ chế
    """

    if request.method != "POST":
        return redirect("processing_list")

    employee_code = request.POST.get("employee_code")
    employee_name = request.POST.get("employee_name")
    employee_position = request.POST.get("employee_position")
    start_time_value = request.POST.get("start_time")
    items_json = request.POST.get("items_json")
    business_date = parse_business_date(request.POST.get("business_date"))

    if not employee_code or not employee_name:
        messages.error(request, "Vui lòng chọn nhân viên sơ chế.")
        return redirect("processing_list")

    if not items_json:
        messages.error(request, "Vui lòng thêm ít nhất một sản phẩm SC thủ công.")
        return redirect("processing_list")

    try:
        items = json.loads(items_json)
    except Exception:
        messages.error(request, "Dữ liệu sản phẩm SC thủ công không hợp lệ.")
        return redirect("processing_list")

    if not items:
        messages.error(request, "Vui lòng thêm ít nhất một sản phẩm SC thủ công.")
        return redirect("processing_list")

    start_time = parse_start_time(start_time_value)
    end_time = timezone.now()
    total_hours = round((end_time - start_time).total_seconds() / 3600, 2)

    shift1_start = parse_shift_datetime(request.POST.get("shift1_start"))
    shift1_end = parse_shift_datetime(request.POST.get("shift1_end"))
    shift2_start = parse_shift_datetime(request.POST.get("shift2_start"))
    shift2_end = parse_shift_datetime(request.POST.get("shift2_end"))

    shift1_hours = calc_shift_hours(shift1_start, shift1_end)
    shift2_hours = calc_shift_hours(shift2_start, shift2_end)

    total_work_hours = round(shift1_hours + shift2_hours, 2)
    overtime_hours = round(max(total_work_hours - 8, 0), 2)

    work_note = request.POST.get("work_note", "")

    ticket = ProcessingTicket.objects.create(
        ticket_code=generate_manual_processing_code(),
        employee_code=employee_code,
        employee_name=employee_name,
        employee_position=employee_position,
        start_time=start_time,
        end_time=end_time,
        total_hours=total_hours,
        business_date=business_date,

        shift1_start=shift1_start,
        shift1_end=shift1_end,
        shift1_hours=shift1_hours,

        shift2_start=shift2_start,
        shift2_end=shift2_end,
        shift2_hours=shift2_hours,

        total_work_hours=total_work_hours,
        overtime_hours=overtime_hours,
        work_note=work_note,
    )

    for item in items:
        raw_stock_id = item.get("raw_stock_id")

        raw_stock = (
            InventoryStock.objects
            .select_for_update()
            .filter(
                id=raw_stock_id,
                warehouse_type="RAW",
            )
            .first()
        )

        if not raw_stock:
            raise Exception("Không tìm thấy sản phẩm trong kho nguyên liệu.")

        received_quantity = float(item.get("received_quantity") or 0)
        processed_stems = float(item.get("processed_stems") or 0)
        damaged_stems = float(item.get("damaged_stems") or 0)
        odd_stems = float(item.get("odd_stems") or 0)
        extra_stems = float(item.get("extra_stems") or 0)
        final_stems = float(item.get("final_stems") or 0)
        final_bunches = float(item.get("final_bunches") or 0)
        stems_per_bunch = int(item.get("stems_per_bunch") or 0)

        if received_quantity <= 0:
            raise Exception(f"Sản phẩm {raw_stock.product_name} chưa có số lượng nhận.")

        if processed_stems <= 0:
            raise Exception(f"Sản phẩm {raw_stock.product_name} chưa có số lượng cành sơ chế.")

        if float(raw_stock.quantity or 0) < received_quantity:
            raise Exception(
                f"Sản phẩm {raw_stock.product_name} không đủ tồn kho. "
                f"Tồn hiện tại: {raw_stock.quantity}, số lượng nhận: {received_quantity}"
            )

        ticket_item = ProcessingTicketItem.objects.create(
            ticket=ticket,
            lot=raw_stock.lot,
            raw_stock_id=raw_stock.id,

            product_group=raw_stock.product_group,
            product_code=raw_stock.product_code,
            product_name=raw_stock.product_name,
            unit=raw_stock.unit,
            flower_grade=raw_stock.flower_grade,

            supplier_code=raw_stock.supplier_code,
            supplier_name=raw_stock.supplier_name,
            received_date=raw_stock.received_date,
            soaking_days=int(item.get("soaking_days") or 0),

            stock_quantity=float(item.get("stock_quantity") or 0),
            received_quantity=received_quantity,

            bunch_type=item.get("bunch_type", ""),
            stems_per_bunch=stems_per_bunch,

            processed_stems=processed_stems,
            damaged_stems=damaged_stems,
            odd_stems=odd_stems,
            extra_stems=extra_stems,

            final_stems=final_stems,
            final_bunches=final_bunches,
        )

        # 1. Trừ kho nguyên liệu
        raw_stock.quantity = float(raw_stock.quantity or 0) - received_quantity
        raw_stock.save()

        InventoryTransaction.objects.create(
            transaction_code=generate_transaction_code(),
            transaction_type="OUT",
            warehouse_type="RAW",

            product_group=raw_stock.product_group,
            product_code=raw_stock.product_code,
            product_name=raw_stock.product_name,
            unit=raw_stock.unit,
            flower_grade=raw_stock.flower_grade,

            supplier_code=raw_stock.supplier_code,
            supplier_name=raw_stock.supplier_name,
            received_date=raw_stock.received_date,

            quantity=received_quantity,
            reference_code=ticket.ticket_code,
            business_date=business_date,
            note=f"Xuất nguyên liệu cho SC thủ công - NV: {employee_name}",
        )

        if raw_stock.lot:
            add_trace_log(
                lot=raw_stock.lot,
                action="move_to_processing",
                quantity=received_quantity,
                from_area="Kho nguyên liệu",
                to_area="Khu sơ chế",
                employee_name=employee_name,
                related_code=ticket.ticket_code,
                note="Xuất nguyên liệu đi SC thủ công",
            )

        # 2. Nhập kho thành phẩm
        finished_stems = final_bunches * stems_per_bunch

        if finished_stems > 0:
            finished_unit = raw_stock.unit or "Cành"

            finished_stock, created = InventoryStock.objects.get_or_create(
                warehouse_type="FINISHED",
                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                flower_grade=raw_stock.flower_grade,
                supplier_code=raw_stock.supplier_code,
                received_date=raw_stock.received_date,
                defaults={
                    "product_name": raw_stock.product_name,
                    "unit": finished_unit,
                    "supplier_name": raw_stock.supplier_name,
                    "quantity": 0,
                    "lot": raw_stock.lot,
                }
            )

            finished_stock.product_name = raw_stock.product_name
            finished_stock.unit = finished_unit
            finished_stock.supplier_name = raw_stock.supplier_name
            finished_stock.quantity = float(finished_stock.quantity or 0) + finished_stems

            if not finished_stock.lot:
                finished_stock.lot = raw_stock.lot

            finished_stock.save()

            InventoryTransaction.objects.create(
                transaction_code=generate_transaction_code(),
                transaction_type="IN",
                warehouse_type="FINISHED",

                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                product_name=raw_stock.product_name,
                unit=finished_unit,
                flower_grade=raw_stock.flower_grade,

                supplier_code=raw_stock.supplier_code,
                supplier_name=raw_stock.supplier_name,
                received_date=raw_stock.received_date,

                quantity=finished_stems,
                reference_code=ticket.ticket_code,
                business_date=business_date,
                note=(
                    f"Nhập kho thành phẩm từ SC thủ công - NV: {employee_name}. "
                    f"{final_bunches} bó x {stems_per_bunch} cành/bó = {finished_stems} cành"
                ),
            )

            if raw_stock.lot:
                add_trace_log(
                    lot=raw_stock.lot,
                    action="processing_done",
                    quantity=finished_stems,
                    from_area="Khu sơ chế",
                    to_area="Kho thành phẩm",
                    employee_name=employee_name,
                    related_code=ticket.ticket_code,
                    note=(
                        f"SC thủ công nhập kho thành phẩm: "
                        f"{final_bunches} bó x {stems_per_bunch} cành/bó = {finished_stems} cành"
                    ),
                )

        # 3. Lưu cành lẻ
        if odd_stems > 0:
            LooseStemStock.objects.create(
                lot=raw_stock.lot,
                processing_item=ticket_item,

                product_code=raw_stock.product_code,
                product_name=raw_stock.product_name,
                product_group=raw_stock.product_group,

                supplier_code=raw_stock.supplier_code,
                supplier_name=raw_stock.supplier_name,

                employee_code=employee_code,
                employee_name=employee_name,

                stems_per_bunch=stems_per_bunch,
                original_quantity=odd_stems,
                remaining_quantity=odd_stems,

                is_carried_next_day=False,
                carry_date=None,

                status="available",
            )

        # 4. Nhập kho hủy
        if damaged_stems > 0:
            damaged_stock, created = InventoryStock.objects.get_or_create(
                warehouse_type="DAMAGED",
                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                flower_grade=raw_stock.flower_grade,
                supplier_code=raw_stock.supplier_code,
                received_date=raw_stock.received_date,
                defaults={
                    "product_name": raw_stock.product_name,
                    "unit": raw_stock.unit,
                    "supplier_name": raw_stock.supplier_name,
                    "quantity": 0,
                    "lot": raw_stock.lot,
                }
            )

            damaged_stock.product_name = raw_stock.product_name
            damaged_stock.unit = raw_stock.unit
            damaged_stock.supplier_name = raw_stock.supplier_name
            damaged_stock.quantity = float(damaged_stock.quantity or 0) + damaged_stems

            if not damaged_stock.lot:
                damaged_stock.lot = raw_stock.lot

            damaged_stock.save()

            InventoryTransaction.objects.create(
                transaction_code=generate_transaction_code(),
                transaction_type="IN",
                warehouse_type="DAMAGED",

                product_group=raw_stock.product_group,
                product_code=raw_stock.product_code,
                product_name=raw_stock.product_name,
                unit=raw_stock.unit,
                flower_grade=raw_stock.flower_grade,

                supplier_code=raw_stock.supplier_code,
                supplier_name=raw_stock.supplier_name,
                received_date=raw_stock.received_date,

                quantity=damaged_stems,
                reference_code=ticket.ticket_code,
                business_date=business_date,
                note=f"Hao hụt/xả hủy từ SC thủ công - NV: {employee_name}",
            )

            if raw_stock.lot:
                add_trace_log(
                    lot=raw_stock.lot,
                    action="processing_waste",
                    quantity=damaged_stems,
                    from_area="Khu sơ chế",
                    to_area="Hoa/Lá phụ hủy",
                    employee_name=employee_name,
                    related_code=ticket.ticket_code,
                    note="Xả/hủy trong quá trình SC thủ công",
                )

    messages.success(
        request,
        "Đã hoàn thành phiếu SC thủ công và cập nhật kho thành phẩm."
    )
    return redirect("processing_list")