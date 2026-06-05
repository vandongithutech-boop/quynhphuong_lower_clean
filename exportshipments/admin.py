from django.contrib import admin
from .models import ExportShipment
from .services import write_trace_logs_for_shipment


@admin.register(ExportShipment)
class ExportShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "shipment_code",
        "export_date",
        "customer_name",
        "vehicle_info",
        "container_code",
        "driver_name",
        "created_at",
    )

    search_fields = (
        "shipment_code",
        "customer_code",
        "customer_name",
        "vehicle_info",
        "container_code",
        "driver_name",
    )

    list_filter = (
        "export_date",
        "created_at",
    )

    filter_horizontal = ("boxes",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        write_trace_logs_for_shipment(form.instance)