from django.contrib import admin
from .models import (
    InventoryReceipt,
    InventoryReceiptItem,
    InventoryStock,
    InventoryTransaction,
    InventoryStockOut,
    InventoryStockOutItem
)


class InventoryReceiptItemInline(admin.TabularInline):
    model = InventoryReceiptItem
    extra = 0


@admin.register(InventoryReceipt)
class InventoryReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_code',
        'product_group',
        'supplier_code',
        'supplier_name',
        'receipt_datetime',
    )

    search_fields = (
        'receipt_code',
        'supplier_code',
        'supplier_name',
    )

    list_filter = (
        'product_group',
        'receipt_datetime',
    )

    inlines = [InventoryReceiptItemInline]


@admin.register(InventoryReceiptItem)
class InventoryReceiptItemAdmin(admin.ModelAdmin):
    list_display = (
        'receipt',
        'product_code',
        'product_name',
        'unit',
        'flower_grade',
        'quantity',
    )

    search_fields = (
        'product_code',
        'product_name',
    )


@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = (
        'warehouse_type',
        'product_group',
        'product_code',
        'product_name',
        'unit',
        'flower_grade',
        'quantity',
        'updated_at',
    )

    search_fields = (
        'product_code',
        'product_name',
    )

    list_filter = (
        'warehouse_type',
        'product_group',
    )


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_code',
        'transaction_type',
        'warehouse_type',
        'product_group',
        'product_code',
        'product_name',
        'quantity',
        'reference_code',
        'business_date',
        'created_at',
    )

    search_fields = (
        'transaction_code',
        'reference_code',
        'product_code',
        'product_name',
    )

    list_filter = (
        'transaction_type',
        'warehouse_type',
        'product_group',
        'created_at',
        'business_date',
    )

class InventoryStockOutItemInline(admin.TabularInline):
    model = InventoryStockOutItem
    extra = 0


@admin.register(InventoryStockOut)
class InventoryStockOutAdmin(admin.ModelAdmin):
    list_display = (
        "stock_out_code",
        "stock_out_type",
        "employee_name",
        "stock_out_datetime",
        "created_at",
    )

    search_fields = (
        "stock_out_code",
        "employee_name",
        "employee_code",
        "items__product_code",
        "items__product_name",
        "items__supplier_name",
    )

    list_filter = (
        "stock_out_type",
        "stock_out_datetime",
        "created_at",
    )

    inlines = [InventoryStockOutItemInline]


@admin.register(InventoryStockOutItem)
class InventoryStockOutItemAdmin(admin.ModelAdmin):
    list_display = (
        "stock_out",
        "product_name",
        "source_warehouse",
        "destination_warehouse",
        "quantity",
        "reason",
        "created_at",
    )

    search_fields = (
        "product_code",
        "product_name",
        "supplier_name",
        "reason",
        "lot__lot_code",
    )

    list_filter = (
        "source_warehouse",
        "destination_warehouse",
        "created_at",
    )