from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

from orders.models import Order
from inventory.models import InventoryReceiptItem
from processing.models import ProcessingTicketItem
from production.models import ProductionOrder
from django.db.models import Q
from django.db.models import Count


def model_has_field(model, field_name):
    return any(field.name == field_name for field in model._meta.get_fields())


def dashboard(request):
    today = timezone.localdate()
    start_day = today - timedelta(days=6)

    # Tổng đơn hàng
    total_orders = Order.objects.count()

    # Đơn hàng đang xử lý
    processing_orders = 0
    if model_has_field(Order, "status"):
        processing_orders = Order.objects.filter(
            status__in=["pending", "processing", "packing", "waiting"]
        ).count()

    # Tồn kho nguyên liệu
    inventory_items = InventoryReceiptItem.objects.count()

    # Sơ chế hôm nay
    today_stems = 0
    today_bunches = 0

    if model_has_field(ProcessingTicketItem, "created_at"):
        processing_today = ProcessingTicketItem.objects.filter(created_at__date=today)
    else:
        processing_today = ProcessingTicketItem.objects.all()

    if model_has_field(ProcessingTicketItem, "final_stems"):
        today_stems = processing_today.aggregate(total=Sum("final_stems"))["total"] or 0

    if model_has_field(ProcessingTicketItem, "final_bunches"):
        today_bunches = processing_today.aggregate(total=Sum("final_bunches"))["total"] or 0

    # Sản xuất hôm nay
    if model_has_field(ProductionOrder, "created_at"):
        production_today = ProductionOrder.objects.filter(created_at__date=today).count()
    else:
        production_today = ProductionOrder.objects.count()

    # Doanh thu 7 ngày
    chart_labels = []
    chart_values = []

    for i in range(7):
        day = start_day + timedelta(days=i)
        chart_labels.append(day.strftime("%d/%m"))

        total = 0
        if model_has_field(Order, "created_at") and model_has_field(Order, "total_amount"):
            total = (
                Order.objects
                .filter(created_at__date=day)
                .aggregate(total=Sum("total_amount"))["total"] or 0
            )

        chart_values.append(float(total))

    latest_orders = Order.objects.all().order_by("-id")[:5]
    # =========================
    # CẢNH BÁO ĐƠN HÀNG
    # =========================
    waiting_orders = 0
    packing_orders = 0
    completed_orders = 0

    if model_has_field(Order, "status"):
        waiting_orders = Order.objects.filter(
            status__in=["pending", "waiting"]
        ).count()

        packing_orders = Order.objects.filter(
            status__in=["packing"]
        ).count()

        completed_orders = Order.objects.filter(
            status__in=["completed", "done"]
        ).count()

    # =========================
    # CẢNH BÁO KHO NGUYÊN LIỆU
    # =========================
    old_inventory_count = 0
    low_inventory_count = 0

    if model_has_field(InventoryReceiptItem, "created_at"):
        old_day = today - timedelta(days=3)
        old_inventory_count = InventoryReceiptItem.objects.filter(
            created_at__date__lte=old_day
        ).count()

    if model_has_field(InventoryReceiptItem, "quantity"):
        low_inventory_count = InventoryReceiptItem.objects.filter(
            quantity__lte=10
        ).count()

    # =========================
    # LỆNH SẢN XUẤT ĐANG CHỜ
    # =========================
    waiting_productions = 0
    # =========================
    # PACKING ĐANG HOẠT ĐỘNG
    # =========================
    active_packing = 0

    if model_has_field(ProductionOrder, "status"):
        active_packing = ProductionOrder.objects.filter(
            status="packing"
        ).count()

    # =========================
    # TOP KHÁCH HÀNG
    # =========================
    top_customers = []

    if model_has_field(Order, "customer"):
        top_customers = (
            Order.objects
            .values("customer")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

    # =========================
    # HOẠT ĐỘNG GẦN ĐÂY
    # =========================
    recent_activities = []

    latest_order_items = Order.objects.order_by("-id")[:5]

    for item in latest_order_items:
        recent_activities.append({
            "title": f"Đơn hàng #{item.id}",
            "desc": "Đơn hàng mới được tạo trong hệ thống."
        })

    if model_has_field(ProductionOrder, "status"):
        waiting_productions = ProductionOrder.objects.filter(
            status__in=["waiting", "pending", "processing", "packing"]
        ).count()

    context = {
        "total_orders": total_orders,
        "processing_orders": processing_orders,
        "inventory_items": inventory_items,
        "today_stems": today_stems,
        "today_bunches": today_bunches,
        "production_today": production_today,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "latest_orders": latest_orders,
        "waiting_orders": waiting_orders,
        "packing_orders": packing_orders,
        "completed_orders": completed_orders,
        "old_inventory_count": old_inventory_count,
        "low_inventory_count": low_inventory_count,
        "waiting_productions": waiting_productions,
        "active_packing": active_packing,
        "top_customers": top_customers,
        "recent_activities": recent_activities,
    }

    return render(request, "dashboard/dashboard.html", context)