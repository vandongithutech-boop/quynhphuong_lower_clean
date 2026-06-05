import json
import random
import string

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum
from processing.models import ProcessingTicketItem
from categories.models import Customer, FlowerType
from .models import Order, OrderItem
from inventory.models import InventoryStock

from traceability.models import TraceLot
from traceability.services import add_trace_log



def get_value(obj, fields):
    for field in fields:
        if hasattr(obj, field):
            value = getattr(obj, field)
            if value:
                return value
    return ""


def generate_order_code():
    today = timezone.now().strftime("%d%m%y")
    random_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"DH{today}{random_code}"


def order_list(request):
    q = request.GET.get("q", "")
    status = request.GET.get("status", "all")

    orders = Order.objects.prefetch_related("items").all()

    if q:
        orders = orders.filter(
            Q(order_code__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_code__icontains=q) |
            Q(customer_phone__icontains=q) |
            Q(items__product_name__icontains=q)
        ).distinct()

    if status != "all":
        orders = orders.filter(status=status)

    today = timezone.localdate()

    context = {
        "orders": orders.order_by("-order_time"),
        "q": q,
        "status": status,
        "total_orders": Order.objects.count(),
        "today_orders": Order.objects.filter(order_time__date=today).count(),
        "processing_orders": Order.objects.filter(status="processing").count(),
        "completed_orders": Order.objects.filter(status="completed").count(),
        "new_order_code": generate_order_code(),
        "now_time": timezone.now(),
    }

    return render(request, "orders/order_list.html", context)


def order_create(request):
    if request.method == "POST":
        print("POST product_name:", request.POST.getlist("product_name[]"))
        print("POST product_code:", request.POST.getlist("product_code[]"))
        print("POST standard_quantity:", request.POST.getlist("standard_quantity[]"))
        print("POST sale_quantity:", request.POST.getlist("sale_quantity[]"))

    if request.method != "POST":
        return redirect("orders:order_list")
    order = Order.objects.create(
        order_code=request.POST.get("order_code"),
        customer_code=request.POST.get("customer_code"),
        customer_name=request.POST.get("customer_name"),
        customer_address=request.POST.get("customer_address"),
        customer_area=request.POST.get("customer_area"),
        customer_phone=request.POST.get("customer_phone"),
        created_by=request.POST.get("created_by"),
        order_time=timezone.now(),
        status="new",
    )

    product_names = request.POST.getlist("product_name[]")
    product_codes = request.POST.getlist("product_code[]")
    flower_types = request.POST.getlist("flower_type[]")
    group_names = request.POST.getlist("group_name[]")
    units = request.POST.getlist("unit[]")
    standard_quantities = request.POST.getlist("standard_quantity[]")
    sale_quantities = request.POST.getlist("sale_quantity[]")
    specifications = request.POST.getlist("specification[]")
    supplier_names = request.POST.getlist("supplier_name[]")
    lot_ids = request.POST.getlist("lot_id[]")
    print("POST lot_ids:", lot_ids)

    for i in range(len(product_names)):
        if product_names[i]:
            lot = None
            if i < len(lot_ids) and lot_ids[i]:
                lot = TraceLot.objects.filter(id=lot_ids[i]).first()

            order_item = OrderItem.objects.create(
                order=order,
                lot=lot,
                product_code=product_codes[i],
                product_name=product_names[i],
                flower_type=flower_types[i],
                group_name=group_names[i],
                unit=units[i],
                standard_quantity=standard_quantities[i] or 0,
                sale_quantity=sale_quantities[i] or 0,
                specification=specifications[i],
                supplier_name=supplier_names[i],
            )

            if lot:
                export_qty = float(standard_quantities[i] or 0) + float(sale_quantities[i] or 0)

                add_trace_log(
                    lot=lot,
                    action="export_order",
                    quantity=export_qty,
                    from_area="Kho thành phẩm",
                    to_area="Đơn hàng",
                    employee_name=request.POST.get("created_by") or "",
                    related_code=order.order_code,
                    note=f"Xuất cho đơn hàng {order.order_code} - KH: {order.customer_name}",
                )
    messages.success(request, "Tạo đơn hàng thành công.")
    return redirect("orders:order_list")


def api_customers(request):
    q = request.GET.get("q", "")

    customers = Customer.objects.all()

    if q:
        customers = customers.filter(
            Q(ten_khach_hang__icontains=q) |
            Q(ma_kh__icontains=q) |
            Q(sdt__icontains=q)
        )

    data = []

    for customer in customers[:50]:
        data.append({
            "code": customer.ma_kh or "",
            "name": customer.ten_khach_hang or "",
            "address": customer.dia_chi or "",
            "area": customer.vung or "",
            "phone": customer.sdt or "",
            "transport": customer.van_chuyen or "",
            "receiver": customer.nguoi_nhan_thay or "",
            "tax": customer.ma_so_thue or "",
            "country": customer.country or "",
        })

    return JsonResponse({"customers": data})


def api_flowers(request):
    flower_group = request.GET.get("type", "").strip().upper()
    q = request.GET.get("q", "").strip()

    stocks = InventoryStock.objects.filter(quantity__gt=0).select_related("lot")

    if flower_group == "HH":
        stocks = stocks.filter(
            warehouse_type__in=["FINISHED", "SALE"]
        )

    elif flower_group == "HP":
        stocks = stocks.filter(
            warehouse_type__in=["RAW", "FINISHED"]
        )

    if flower_group:
        flower_codes = FlowerType.objects.filter(
            category_type__iexact=flower_group
        ).values_list("code", flat=True)

        stocks = stocks.filter(
            Q(product_group__iexact=flower_group) |
            Q(product_code__in=flower_codes)
        )

    if q:
        stocks = stocks.filter(
            Q(product_name__icontains=q) |
            Q(product_code__icontains=q) |
            Q(supplier_name__icontains=q)
        )

    data = []

    for stock in stocks.order_by("product_name", "received_date"):
        flower_info = FlowerType.objects.filter(
            code=stock.product_code
        ).first()

        if not flower_info:
            flower_info = FlowerType.objects.filter(
                name__iexact=stock.product_name
            ).first()

        data.append({
            "stock_id": stock.id,
            "lot_id": stock.lot.id if stock.lot else "",
            "lot_code": stock.lot.lot_code if stock.lot else "Chưa có mã lô",
            "code": stock.product_code or "",
            "name": stock.product_name or "",
            "category": flower_info.category_type if flower_info else stock.product_group or "",
            "unit": stock.unit or "",
            "group_name": flower_info.color if flower_info else "",
            "supplier": stock.supplier_name or "",
            "received_date": stock.received_date.strftime("%d/%m/%Y") if stock.received_date else "",
            "total_stems": stock.quantity or 0,
            "total_bunches": 0,
            "warehouse_type": stock.warehouse_type,
        })

    return JsonResponse({"flowers": data})

def api_product_stock(request):
    product_code = request.GET.get("product_code", "")
    product_name = request.GET.get("product_name", "")
    flower_type = request.GET.get("flower_type", "")

    warehouse_types = ["FINISHED", "SALE"]

    if flower_type.upper() == "HP":
        warehouse_types = ["RAW", "FINISHED", "SALE"]

    stocks = InventoryStock.objects.filter(
        warehouse_type__in=warehouse_types,
        quantity__gt=0,
    )

    if product_code:
        stocks = stocks.filter(product_code=product_code)
    elif product_name:
        stocks = stocks.filter(product_name__icontains=product_name)

    total_stems = stocks.aggregate(total=Sum("quantity"))["total"] or 0

    return JsonResponse({
        "total_stems": total_stems,
        "total_bunches": 0,
    })

def api_raw_stock_warning(request):
    product_code = request.GET.get("product_code", "")
    product_name = request.GET.get("product_name", "")
    required_qty = float(request.GET.get("required_qty", 0) or 0)

    raw_stocks = InventoryStock.objects.filter(
        warehouse_type="RAW"
    )

    if product_code:
        raw_stocks = raw_stocks.filter(product_code__icontains=product_code)
    elif product_name:
        raw_stocks = raw_stocks.filter(product_name__icontains=product_name)

    raw_available = raw_stocks.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    can_process_qty = min(required_qty, raw_available)
    still_missing_qty = max(required_qty - raw_available, 0)

    return JsonResponse({
        "raw_available": raw_available,
        "can_process_qty": can_process_qty,
        "still_missing_qty": still_missing_qty,
    })
