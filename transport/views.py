from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from purchases.models import PurchaseOrder
from .models import TransportRoute, TransportCompany, VehicleInspection
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from purchases.models import PurchaseOrderItem

from purchases.models import PurchaseOrderAlert

def transport_list(request):
    keyword = request.GET.get('q', '')
    view_type = request.GET.get('type', 'all')

    if request.method == "POST" and request.POST.get("form_type") == "vehicle_inspection":
        VehicleInspection.objects.create(
            check_date=request.POST.get("check_date"),
            check_time=request.POST.get("check_time"),

            tire_ok=bool(request.POST.get("tire_ok")),
            tire_note=request.POST.get("tire_note", ""),

            box_ok=bool(request.POST.get("box_ok")),
            box_note=request.POST.get("box_note", ""),

            oil_ok=bool(request.POST.get("oil_ok")),
            oil_note=request.POST.get("oil_note", ""),

            windshield_ok=bool(request.POST.get("windshield_ok")),
            windshield_note=request.POST.get("windshield_note", ""),

            fuel_ok=bool(request.POST.get("fuel_ok")),
            fuel_percent=request.POST.get("fuel_percent") or None,
            fuel_note=request.POST.get("fuel_note", ""),

            light_ok=bool(request.POST.get("light_ok")),
            light_note=request.POST.get("light_note", ""),

            horn_ok=bool(request.POST.get("horn_ok")),
            horn_note=request.POST.get("horn_note", ""),

            gps_ok=bool(request.POST.get("gps_ok")),
            gps_note=request.POST.get("gps_note", ""),
        )

        messages.success(request, "Đã lưu phiếu kiểm tra xe thành công.")
        return redirect("transport:transport_list")

    routes = TransportRoute.objects.filter(is_active=True).prefetch_related(
        "route_companies__company"
    )

    companies = TransportCompany.objects.filter(is_active=True)

    if keyword:
        if view_type == "company":
            companies = companies.filter(name__icontains=keyword)
        else:
            routes = routes.filter(name__icontains=keyword)
            companies = companies.filter(name__icontains=keyword)

    now = timezone.localtime()

    context = {
        "routes": routes,
        "companies": companies,
        "keyword": keyword,
        "view_type": view_type,

        # thống kê tạm
        "total_purchase_orders": 0,
        "pending_purchase_orders": 0,
        "today_purchase_orders": 0,
        "completed_purchase_orders": 0,
    }

    return render(request, "transport/transport_list.html", context)


def transport_dashboard(request):
    routes = TransportRoute.objects.filter(is_active=True)
    companies = TransportCompany.objects.filter(is_active=True)

    purchase_orders = (
        PurchaseOrder.objects
        .prefetch_related("items")
        .filter(status__in=["draft", "assigned_driver"])
        .order_by("-order_datetime")
    )

    for po in purchase_orders:
        supplier_names = set()

        for item in po.items.all():
            if item.supplier_name:
                supplier_names.add(item.supplier_name.strip())
            elif po.supplier_name:
                supplier_names.add(po.supplier_name.strip())

        po.transport_supplier_display = (
            "Đơn hàng hỗn hợp" if len(supplier_names) >= 2 else po.supplier_name
        )

    context = {
        "routes": routes,
        "companies": companies,
        "purchase_orders": purchase_orders,
        "total_purchase_orders": purchase_orders.count(),
        "pending_purchase_orders": purchase_orders.filter(status="draft").count(),
        "today_purchase_orders": purchase_orders.filter(
            order_datetime__date=timezone.localdate()
        ).count(),
        "completed_purchase_orders": PurchaseOrder.objects.filter(status="received").count(),
    }

    return render(request, "transport/transport_dashboard.html", context)

@login_required
def accept_purchase_order(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)

    if request.method == "POST":
        full_name = request.user.get_full_name() or request.user.username

        po.driver_name = full_name
        po.driver_employee_code = request.user.username
        po.driver_confirmed_at = timezone.now()
        po.status = "assigned_driver"
        po.save()

        messages.success(request, f"Bạn đã nhận đơn {po.po_code}.")

    return redirect("transport:transport_dashboard")


@login_required
def complete_purchase_order(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)

    if request.method == "POST":
        po.status = "waiting_stock_in"
        po.save()

        messages.success(request, f"Đơn {po.po_code} đã hoàn thành vận chuyển, chờ nhập kho.")

    return redirect("transport:transport_dashboard")

@login_required
@require_POST
def driver_confirm_purchase_item(request, item_id):
    item = get_object_or_404(PurchaseOrderItem, id=item_id)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({
            "success": False,
            "message": "Dữ liệu gửi lên không hợp lệ."
        }, status=400)

    driver_received_quantity = data.get("driver_received_quantity")
    driver_confirmed = data.get("driver_confirmed", False)

    item.driver_received_quantity = driver_received_quantity or 0
    item.driver_confirmed = bool(driver_confirmed)

    if item.driver_confirmed:
        item.driver_confirmed_at = timezone.now()
    else:
        item.driver_confirmed_at = None

    item.save()
    if float(driver_received_quantity or 0) > float(item.ordered_quantity or 0):
        PurchaseOrderAlert.objects.update_or_create(
            item=item,
            status="pending",
            defaults={
                "purchase_order": item.purchase_order,
                "product_name": item.product_name,
                "ordered_quantity": item.ordered_quantity,
                "driver_received_quantity": driver_received_quantity,
                "driver_name": item.purchase_order.driver_name,
                "supplier_name": item.supplier_name or item.purchase_order.supplier_name,
                "message": (
                    f"Sản phẩm {item.product_name} nhận thực tế {driver_received_quantity}, "
                    f"cao hơn số lượng đặt {item.ordered_quantity}."
                ),
            }
        )
    return JsonResponse({
        "success": True,
        "driver_confirmed": item.driver_confirmed,
        "driver_received_quantity": item.driver_received_quantity,
        "driver_confirmed_at": item.driver_confirmed_at.strftime("%d/%m/%Y %H:%M") if item.driver_confirmed_at else "",
    })

@login_required
def driver_alert_results(request):
    driver_name = request.user.get_full_name() or request.user.username

    alerts = (
        PurchaseOrderAlert.objects
        .filter(status__in=["approved", "rejected"])
        .filter(purchase_order__driver_name=driver_name)
        .select_related("purchase_order", "item")
        .order_by("-resolved_at")[:10]
    )

    data = []

    for alert in alerts:
        data.append({
            "id": alert.id,
            "status": alert.status,
            "po_code": alert.purchase_order.po_code,
            "product_name": alert.product_name,
            "ordered_quantity": alert.ordered_quantity,
            "driver_received_quantity": alert.driver_received_quantity,
            "approved_quantity": alert.approved_quantity,
            "resolved_at": alert.resolved_at.strftime("%d/%m/%Y %H:%M") if alert.resolved_at else "",
        })

    return JsonResponse({
        "success": True,
        "alerts": data,
    })

@login_required
def complete_purchase_order(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)

    if request.method == "POST":
        if po.alerts.filter(status="pending").exists():
            messages.error(request, "Đơn còn cảnh báo vượt số lượng chưa được xử lý.")
            return redirect("transport:transport_dashboard")

        if po.items.filter(driver_confirmed=False).exists():
            messages.error(request, "Vui lòng tick xác nhận đủ tất cả sản phẩm trước khi hoàn thành.")
            return redirect("transport:transport_dashboard")

        po.status = "waiting_stock_in"
        po.save(update_fields=["status"])

        messages.success(request, f"Đã hoàn thành đơn {po.po_code} và chuyển sang Kho tổng chờ nhập kho.")

    return redirect("transport:transport_dashboard")