from django.urls import path
from . import views

app_name = "purchases"

urlpatterns = [
    path("", views.purchase_order_list, name="purchase_order_list"),
    path("create/", views.create_purchase_order, name="create_purchase_order"),
    path("alerts/pending/", views.pending_purchase_alerts, name="pending_purchase_alerts"),
    path("alerts/<int:alert_id>/approve/", views.approve_purchase_alert, name="approve_purchase_alert"),
    path("alerts/<int:alert_id>/reject/", views.reject_purchase_alert, name="reject_purchase_alert"),
    ]