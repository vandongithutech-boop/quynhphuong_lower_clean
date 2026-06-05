from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_code",
        "customer_name",
        "employee_name",
        "transport_vehicle",
        "order_time",
        "status",
    )

    search_fields = (
        "order_code",
        "customer_name",
        "employee_name",
        "transport_vehicle",
    )

    list_filter = ("status", "order_time")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "flower_type",
        "supplier_name",
        "standard_quantity",
        "sale_quantity",
        "unit",
        "specification",
    )

    search_fields = (
        "order__order_code",
        "product_name",
        "flower_type",
        "supplier_name",
    )