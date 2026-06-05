from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),

    path('nhap-kho/', views.create_stock_in, name='create_stock_in'),
    path("raw-materials/", views.raw_material_inventory, name="raw_material_inventory"),

    path('hoa-hong/', views.rose_inventory, name='rose_inventory'),
    path('hoa-la-phu/', views.flower_leaf_inventory, name='flower_leaf_inventory'),
    path('kho-sale/', views.sale_inventory, name='sale_inventory'),
    path('vat-tu/', views.material_inventory, name='material_inventory'),
    path('thanh-pham/', views.finished_inventory, name='finished_inventory'),
    path('nguyen-lieu/', views.raw_inventory, name='raw_inventory'),
    path('xuat-kho/', views.create_stock_out, name='create_stock_out'),
    path('api/xuat-kho/products/', views.api_stock_out_products, name='api_stock_out_products'),
    path('hoa-huy/', views.damaged_inventory, name='damaged_inventory'),
    path("api/pending-stock-in-orders/",views.api_pending_stock_in_orders,name="api_pending_stock_in_orders"),
    path('nhap-kho-tu-don/<int:po_id>/',views.create_stock_in_from_purchase_order,name='create_stock_in_from_purchase_order'),
    path('tao-qr-bo-tu-don/<int:po_id>/',views.create_bundle_labels_from_purchase_order,name='create_bundle_labels_from_purchase_order'),
    path("api/save-warehouse-check/",views.api_save_warehouse_checked_quantity,name="api_save_warehouse_checked_quantity"),
    path("kiem-ke-nhanh/",views.quick_inventory_check,name="quick_inventory_check"),
    path("bao-cao-ton-kho/", views.inventory_stock_report, name="inventory_stock_report"),
    path("bao-cao-ton-kho/excel/",views.export_inventory_stock_report_excel,name="export_inventory_stock_report_excel"
),
]