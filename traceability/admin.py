from django.contrib import admin
from .models import TraceLot, TraceLog, DisposalRecord
from .models import TraceBundle

class TraceLogInline(admin.TabularInline):
    model = TraceLog
    extra = 0
    readonly_fields = ("action", "from_area", "to_area", "quantity", "employee_name", "related_code", "note", "created_at")
    can_delete = False


@admin.register(TraceLot)
class TraceLotAdmin(admin.ModelAdmin):
    list_display = (
        "lot_code",
        "product_name",
        "supplier_name",
        "received_date",
        "received_quantity",
        "delivery_type",
        "created_at",
    )
    search_fields = ("lot_code", "product_code", "product_name", "supplier_code", "supplier_name")
    list_filter = ("delivery_type", "received_date", "created_at")
    readonly_fields = ("created_at", "updated_at", "qr_code")
    inlines = [TraceLogInline]


@admin.register(TraceLog)
class TraceLogAdmin(admin.ModelAdmin):
    list_display = (
        "lot",
        "action",
        "from_area",
        "to_area",
        "quantity",
        "employee_name",
        "related_code",
        "created_at",
    )
    search_fields = ("lot__lot_code", "lot__product_name", "employee_name", "related_code")
    list_filter = ("action", "from_area", "to_area", "created_at")


@admin.register(DisposalRecord)
class DisposalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "lot",
        "quantity",
        "reason",
        "employee_name",
        "created_at",
    )
    search_fields = ("lot__lot_code", "lot__product_name", "reason", "employee_name")
    list_filter = ("created_at",)

@admin.register(TraceBundle)
class TraceBundleAdmin(admin.ModelAdmin):
    list_display = (
        "bundle_code",
        "lot",
        "product_code",
        "product_name",
        "bundle_number",
        "expected_stems",
        "actual_stems",
        "remaining_stems",
        "supplier_name",
        "source_type",
        "seller_name",
        "status",
        "created_at",
    )

    search_fields = (
        "bundle_code",
        "lot__lot_code",
        "product_code",
        "product_name",
        "supplier_name",
        "seller_name",
        "seller_phone",
    )

    list_filter = (
        "status",
        "source_type",
        "supplier_name",
        "created_at",
    )

    readonly_fields = (
        "bundle_code",
        "created_at",
    )