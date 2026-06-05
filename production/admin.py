from django.contrib import admin
from .models import ProductionOrder, ProductionItem, PackingBox
from .models import PackingBoxItem,PackingStemRule,PackingBoxType,ProductPackingRule,PackingIndex,BoxCapacity


class ProductionItemInline(admin.TabularInline):
    model = ProductionItem
    extra = 0


class PackingBoxInline(admin.TabularInline):
    model = PackingBox
    extra = 0


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = (
        "production_code",
        "order_code",
        "customer_name",
        "status",
        "received_at",
    )

    search_fields = (
        "production_code",
        "order_code",
        "customer_name",
    )

    list_filter = ("status", "received_at")
    inlines = [ProductionItemInline, PackingBoxInline]


@admin.register(ProductionItem)
class ProductionItemAdmin(admin.ModelAdmin):
    list_display = (
        "production_order",
        "product_name",
        "standard_quantity",
        "sale_quantity",
        "finished_available",
        "missing_quantity",
        "raw_available",
        "need_processing_quantity",
        "is_sale_item",
    )

    search_fields = (
        "product_code",
        "product_name",
        "production_order__production_code",
    )


@admin.register(PackingBox)
class PackingBoxAdmin(admin.ModelAdmin):
    list_display = (
        "box_code",
        "production_order",
        "box_number",
        "total_bunches",
        "total_stems",
        "nw",
        "gw",
    )


@admin.register(PackingBoxItem)
class PackingBoxItemAdmin(admin.ModelAdmin):
    list_display = (
        "box",
        "product_name",
        "bunches",
        "stems",
        "stems_per_bunch",
        "nw",
        "gw",
    )

@admin.register(PackingStemRule)
class PackingStemRuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "stems_quantity")


@admin.register(PackingBoxType)
class PackingBoxTypeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "max_bunches",
        "max_stems",
        "box_weight",
    )


@admin.register(ProductPackingRule)
class ProductPackingRuleAdmin(admin.ModelAdmin):
    list_display = (
        "flower",
        "stem_rule",
        "box_type",
        "bunches_per_box",
        "nw_per_bunch",
        "is_default",
    )

    list_filter = (
        "flower",
        "stem_rule",
        "box_type",
    )
@admin.register(PackingIndex)
class PackingIndexAdmin(admin.ModelAdmin):
    list_display = (
        "flower",
        "packing_index",
        "base_stems",
        "is_active",
    )

    search_fields = (
        "flower__code",
        "flower__name",
    )

    list_filter = ("is_active",)


@admin.register(BoxCapacity)
class BoxCapacityAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "capacity_index",
        "box_weight",
        "is_active",
    )

    search_fields = ("code", "name")
    list_filter = ("is_active",)