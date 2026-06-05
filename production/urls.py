from django.urls import path
from . import views

app_name = "production"

urlpatterns = [
    path("", views.production_list, name="production_list"),
    path("receive/<int:order_id>/", views.receive_order, name="receive_order"),
    path("status/<int:production_id>/<str:new_status>/", views.update_production_status, name="update_status"),

    path("packing/<int:production_id>/", views.packing_detail, name="packing_detail"),
    path("packing/<int:production_id>/update-qty/", views.update_packing_quantities, name="update_packing_quantities"),
    path("packing/<int:production_id>/create-box/", views.create_packing_box, name="create_packing_box"),

    path("box/<int:box_id>/", views.packing_box_detail, name="packing_box_detail"),

    path("packing-list/<int:production_id>/", views.packing_list_view, name="packing_list"),
    path("packing-list/<int:production_id>/export/", views.export_packing_list_excel, name="export_packing_list_excel"),
    path("packing-box/<int:box_id>/edit/", views.edit_packing_box, name="edit_packing_box"),
    path("packing-box/<int:box_id>/delete/", views.delete_packing_box, name="delete_packing_box"),
    path("packing/<int:production_id>/reset/", views.reset_packing, name="reset_packing"),
    path("packing-list/<int:production_id>/pdf/",views.export_packing_list_pdf,name="export_packing_list_pdf"),
    path("label/<int:box_id>/", views.packing_label_view, name="packing_label"),
    path("api/pending-orders-voice/", views.pending_orders_voice_api, name="pending_orders_voice_api"),
    path("api/suggest-box/", views.suggest_box_api, name="suggest_box_api"),
]