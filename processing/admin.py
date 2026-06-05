from django.contrib import admin

from .models import LooseStemStock, LooseStemMerge, LooseStemMergeItem
@admin.register(LooseStemStock)
class LooseStemStockAdmin(admin.ModelAdmin):
    list_display = (
        "product_code",
        "product_name",
        "supplier_name",
        "employee_name",
        "stems_per_bunch",
        "original_quantity",
        "remaining_quantity",
        "status",
        "created_at",
    )

    search_fields = (
        "product_code",
        "product_name",
        "supplier_name",
        "employee_name",
        "lot__lot_code",
    )

    list_filter = (
        "status",
        "stems_per_bunch",
        "created_at",
    )


class LooseStemMergeItemInline(admin.TabularInline):
    model = LooseStemMergeItem
    extra = 0


@admin.register(LooseStemMerge)
class LooseStemMergeAdmin(admin.ModelAdmin):
    list_display = (
        "merge_code",
        "product_code",
        "product_name",
        "stems_per_bunch",
        "total_stems",
        "total_bunches",
        "created_by",
        "created_at",
    )

    search_fields = (
        "merge_code",
        "product_code",
        "product_name",
        "main_lot__lot_code",
    )

    list_filter = (
        "stems_per_bunch",
        "created_at",
    )

    inlines = [LooseStemMergeItemInline]


@admin.register(LooseStemMergeItem)
class LooseStemMergeItemAdmin(admin.ModelAdmin):
    list_display = (
        "merge",
        "lot",
        "supplier_name",
        "quantity_used",
        "created_at",
    )

    search_fields = (
        "merge__merge_code",
        "lot__lot_code",
        "supplier_name",
    )