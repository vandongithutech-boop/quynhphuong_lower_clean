from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_dashboard, name="dashboard"),

    path(
        "ton-kho/",
        views.inventory_current_report,
        name="inventory_current_report"
    ),

    path(
        "nhap-kho/",
        views.inventory_in_report,
        name="inventory_in_report"
    ),

    path(
        "xuat-kho/",
        views.inventory_out_report,
        name="inventory_out_report"
    ),

    path(
        "ton-kho/excel/",
        views.export_inventory_report_excel,
        name="export_inventory_report_excel"
    ),
]