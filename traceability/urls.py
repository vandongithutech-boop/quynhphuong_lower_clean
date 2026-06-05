from django.urls import path
from . import views

app_name = "traceability"

urlpatterns = [
    path("trace/<str:lot_code>/", views.trace_lot_detail, name="trace_lot_detail"),
    path("trace/box/<int:box_id>/", views.trace_box_detail, name="trace_box_detail"),
]