from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem
from django.contrib import messages
from .services import receive_purchase_order_to_stock
from django.contrib import messages
from .services import receive_purchase_pickup_to_stock
from .models import (PurchasePickup,PurchasePickupItem,)

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "po_code",
        "supplier_name",
        "driver_employee_code",
        "driver_name",
        "vehicle_info",
        "warehouse_receiver_code",
        "warehouse_receiver",
        "order_datetime",
        "pickup_date",
        "received_date",
        "status",
        "created_at",
    )

    search_fields = (
        "po_code",
        "supplier_code",
        "supplier_name",
        "driver_employee_code",
        "driver_name",
        "vehicle_info",
        "warehouse_receiver_code",
        "warehouse_receiver",
    )

    list_filter = (
        "status",
        "order_datetime",
        "pickup_date",
        "received_date",
    )
    actions = [
        "mark_assigned_driver",
        "mark_picked_up",
        "mark_waiting_stock_in",
        "mark_received",
        "mark_cancelled",
        "receive_to_stock",
    ]
@admin.action(description="Nhập kho từ đơn đặt mua")
def receive_to_stock(self, request, queryset):
    success_count = 0

    for po in queryset:
        try:
            receive_purchase_order_to_stock(po, request=request)
            success_count += 1
        except Exception as e:
            self.message_user(
                request,
                f"Lỗi {po.po_code}: {e}",
                level=messages.ERROR
            )

    if success_count:
        self.message_user(
            request,
            f"Đã nhập kho thành công {success_count} đơn đặt mua.",
            level=messages.SUCCESS
        )
@admin.action(description="Chuyển sang: Đã giao tài xế")
def mark_assigned_driver(self, request, queryset):
    queryset.update(status="assigned_driver")

@admin.action(description="Chuyển sang: Đã lấy hàng")
def mark_picked_up(self, request, queryset):
    queryset.update(status="picked_up")

@admin.action(description="Chuyển sang: Chờ nhập kho")
def mark_waiting_stock_in(self, request, queryset):
    queryset.update(status="waiting_stock_in")

@admin.action(description="Chuyển sang: Đã nhập kho")
def mark_received(self, request, queryset):
    queryset.update(status="received")

@admin.action(description="Chuyển sang: Đã hủy")
def mark_cancelled(self, request, queryset):
    queryset.update(status="cancelled")
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_order",
        "product_code",
        "product_name",
        "stems_per_bundle",
        "ordered_quantity",
        "received_quantity",
        "expected_bundle_count",
        "actual_bundle_count",
    )

    search_fields = (
        "purchase_order__po_code",
        "product_code",
        "product_name",
    )

class PurchasePickupItemInline(admin.TabularInline):
    model = PurchasePickupItem
    extra = 0


@admin.register(PurchasePickup)
class PurchasePickupAdmin(admin.ModelAdmin):
    list_display = (
        "pickup_code",
        "purchase_order",
        "driver_employee_code",
        "driver_name",
        "vehicle_info",
        "pickup_date",
        "received_date",
        "warehouse_receiver_code",
        "warehouse_receiver",
        "status",
        "created_at",
    )

    search_fields = (
        "pickup_code",
        "purchase_order__po_code",
        "driver_employee_code",
        "driver_name",
        "vehicle_info",
        "warehouse_receiver_code",
        "warehouse_receiver",
    )

    list_filter = (
        "status",
        "pickup_date",
        "received_date",
        "created_at",
    )

    inlines = [PurchasePickupItemInline]

    actions = [
        "mark_assigned_driver",
        "mark_picked_up",
        "mark_waiting_stock_in",
        "mark_received",
        "mark_cancelled",
        "receive_pickup_to_stock",
    ]
    @admin.action(description="Nhập kho theo chuyến lấy hàng")
    def receive_pickup_to_stock(self, request, queryset):
        success_count = 0

        for pickup in queryset:
            try:
                receive_purchase_pickup_to_stock(pickup, request=request)
                success_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Lỗi {pickup.pickup_code}: {e}",
                    level=messages.ERROR
                )

        if success_count:
            self.message_user(
                request,
                f"Đã nhập kho thành công {success_count} chuyến lấy hàng.",
                level=messages.SUCCESS
            )
    @admin.action(description="Chuyển sang: Đã giao tài xế")
    def mark_assigned_driver(self, request, queryset):
        queryset.update(status="assigned_driver")

    @admin.action(description="Chuyển sang: Đã lấy hàng")
    def mark_picked_up(self, request, queryset):
        queryset.update(status="picked_up")

    @admin.action(description="Chuyển sang: Chờ nhập kho")
    def mark_waiting_stock_in(self, request, queryset):
        queryset.update(status="waiting_stock_in")

    @admin.action(description="Chuyển sang: Đã nhập kho")
    def mark_received(self, request, queryset):
        queryset.update(status="received")

    @admin.action(description="Chuyển sang: Đã hủy")
    def mark_cancelled(self, request, queryset):
        queryset.update(status="cancelled")


@admin.register(PurchasePickupItem)
class PurchasePickupItemAdmin(admin.ModelAdmin):
    list_display = (
        "pickup",
        "purchase_order_item",
        "product_code",
        "product_name",
        "stems_per_bundle",
        "planned_quantity",
        "received_quantity",
        "planned_bundle_count",
        "actual_bundle_count",
    )

    search_fields = (
        "pickup__pickup_code",
        "purchase_order_item__purchase_order__po_code",
        "product_code",
        "product_name",
    )