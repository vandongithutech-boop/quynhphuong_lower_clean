import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from employees.models import Employee
from django.db.models import Q
from categories.models import Customer, FlowerType
from .models import PurchaseOrder, PurchaseOrderItem
from datetime import datetime
from accounts.permissions import can_access_module
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import PurchaseOrderAlert

def purchase_order_list(request):
    purchase_orders = (
        PurchaseOrder.objects
        .prefetch_related("items", "pickups")
        .all()
        .order_by("-created_at")
    )

    suppliers = Customer.objects.filter(
    Q(ma_kh__startswith="NCC") | Q(ma_kh__startswith="KH")
    ).order_by("ma_kh")

    products = FlowerType.objects.all().order_by("name")

    drivers = Employee.objects.filter(
        bo_phan__icontains="Lái xe",
        trang_thai__icontains="Đang làm"
    ).order_by("ho_ten")
    products = FlowerType.objects.all().order_by("name")

    return render(request, "purchases/purchase_order_list.html", {
        "purchase_orders": purchase_orders,
        "suppliers": suppliers,
        "products": products,
        "drivers": drivers,
    })


def create_purchase_order(request):
    if request.method != "POST":
        return redirect("purchases:purchase_order_list")

    supplier_value = request.POST.get("supplier", "").strip()

    order_datetime_value = request.POST.get("order_datetime")
    if order_datetime_value:
        order_datetime = timezone.make_aware(
            datetime.strptime(order_datetime_value, "%Y-%m-%dT%H:%M")
        )
    else:
        order_datetime = timezone.now()

    status = request.POST.get("status") or "draft"

    driver_employee_code = request.POST.get("driver_employee_code", "")
    driver_name = request.POST.get("driver_name", "")
    vehicle_info = request.POST.get("vehicle_info", "")
    note = request.POST.get("note", "")

    items_json = request.POST.get("items_json", "")

    if not supplier_value:
        messages.error(request, "Vui lòng chọn nhà cung cấp.")
        return redirect("purchases:purchase_order_list")

    if not items_json:
        messages.error(request, "Vui lòng thêm ít nhất một sản phẩm.")
        return redirect("purchases:purchase_order_list")

    try:
        items = json.loads(items_json)
    except Exception:
        messages.error(request, "Dữ liệu sản phẩm đặt mua không hợp lệ.")
        return redirect("purchases:purchase_order_list")

    if not items:
        messages.error(request, "Vui lòng thêm ít nhất một sản phẩm.")
        return redirect("purchases:purchase_order_list")

    supplier_code = ""
    supplier_name = supplier_value

    if " - " in supplier_value:
        supplier_code, supplier_name = supplier_value.split(" - ", 1)

    item_supplier_values = []

    for item in items:
        item_supplier = (item.get("supplier") or supplier_value).strip()
        if item_supplier:
            item_supplier_values.append(item_supplier)

    unique_suppliers = list(set(item_supplier_values))
    is_mixed_supplier = len(unique_suppliers) >= 2

    po = PurchaseOrder.objects.create(
        supplier_code="" if is_mixed_supplier else supplier_code,
        supplier_name="Đơn hàng hỗn hợp" if is_mixed_supplier else supplier_name,
        order_datetime=order_datetime,
        status=status,
        driver_employee_code=driver_employee_code,
        driver_name=driver_name,
        vehicle_info=vehicle_info,
        note=note,
    )

    created_items = 0

    for item in items:
        product_code = item.get("product_code", "")
        product_name = item.get("product_name", "")
        unit = item.get("unit", "cành")
        stems_per_bundle = int(float(item.get("stems_per_bundle") or 0))
        ordered_quantity = float(item.get("ordered_quantity") or 0)
        item_note = item.get("note", "")

        item_supplier_value = (item.get("supplier") or supplier_value).strip()
        item_supplier_code = ""
        item_supplier_name = item_supplier_value

        if " - " in item_supplier_value:
            item_supplier_code, item_supplier_name = item_supplier_value.split(" - ", 1)

        if not product_code or not product_name or ordered_quantity <= 0:
            continue

        PurchaseOrderItem.objects.create(
            purchase_order=po,
            supplier_code=item_supplier_code,
            supplier_name=item_supplier_name,
            product_code=product_code,
            product_name=product_name,
            unit=unit,
            stems_per_bundle=stems_per_bundle,
            ordered_quantity=ordered_quantity,
            note=item_note,
            over_quantity_status="none",
        )

        created_items += 1

    if created_items <= 0:
        po.delete()
        messages.error(request, "Không có sản phẩm hợp lệ để tạo đơn đặt mua.")
        return redirect("purchases:purchase_order_list")

    messages.success(
        request,
        f"Đã tạo đơn đặt mua {po.po_code} với {created_items} sản phẩm."
    )
    return redirect("purchases:purchase_order_list")

def user_is_accounting(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    username = user.username

    try:
        employee = Employee.objects.filter(ma_nv=username).first()

        if not employee:
            return False

        bo_phan = (employee.bo_phan or "").upper()
        chuc_vu = (employee.chuc_vu or "").upper()

        return "KE_TOAN" in bo_phan or "KẾ TOÁN" in bo_phan or "KE_TOAN" in chuc_vu or "KẾ TOÁN" in chuc_vu

    except Exception:
        return False

def pending_purchase_alerts(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": True,
            "alerts": [],
        })

    if not can_access_module(request.user, "purchase_alerts"):
        return JsonResponse({
            "success": True,
            "alerts": [],
        })

    alerts = PurchaseOrderAlert.objects.filter(status="pending").select_related(
        "purchase_order",
        "item",
    )

    data = []

    for alert in alerts:
        data.append({
            "id": alert.id,
            "po_code": alert.purchase_order.po_code,
            "product_name": alert.product_name,
            "supplier_name": alert.supplier_name or alert.item.supplier_name or alert.purchase_order.supplier_name,
            "driver_name": alert.driver_name or alert.purchase_order.driver_name or "Chưa xác định",
            "ordered_quantity": alert.ordered_quantity,
            "driver_received_quantity": alert.driver_received_quantity,
            "message": alert.message,
        })

    return JsonResponse({
        "success": True,
        "alerts": data,
    })


def reject_purchase_alert(request, alert_id):
    alert = get_object_or_404(PurchaseOrderAlert, id=alert_id)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = {}

    approved_quantity = data.get("approved_quantity")

    if approved_quantity in [None, ""]:
        return JsonResponse({
            "success": False,
            "message": "Vui lòng nhập số lượng được phép nhận."
        }, status=400)

    approved_quantity = float(approved_quantity)

    alert.status = "rejected"
    alert.approved_quantity = approved_quantity
    alert.resolved_at = timezone.now()
    alert.save()

    alert.item.driver_received_quantity = approved_quantity
    alert.item.over_quantity_status = "rejected"
    alert.item.save()

    return JsonResponse({
        "success": True,
        "approved_quantity": approved_quantity,
    })


def reject_purchase_alert(request, alert_id):
    alert = get_object_or_404(PurchaseOrderAlert, id=alert_id)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = {}

    approved_quantity = data.get("approved_quantity")

    if approved_quantity in [None, ""]:
        return JsonResponse({
            "success": False,
            "message": "Vui lòng nhập số lượng được phép nhận."
        }, status=400)

    approved_quantity = float(approved_quantity)

    alert.status = "rejected"
    alert.approved_quantity = approved_quantity
    alert.resolved_at = timezone.now()
    alert.save()

    alert.item.driver_received_quantity = approved_quantity
    alert.item.save()

    return JsonResponse({
        "success": True,
        "approved_quantity": approved_quantity,
    })

def approve_purchase_alert(request, alert_id):
    alert = get_object_or_404(PurchaseOrderAlert, id=alert_id)

    alert.status = "approved"
    alert.approved_quantity = alert.driver_received_quantity
    alert.resolved_at = timezone.now()
    alert.save()

    alert.item.driver_received_quantity = alert.driver_received_quantity
    alert.item.over_quantity_status = "approved"
    alert.item.save()

    return JsonResponse({
        "success": True,
        "approved_quantity": alert.approved_quantity,
    })