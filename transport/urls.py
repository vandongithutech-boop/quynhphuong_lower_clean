from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    path('', views.transport_dashboard, name='transport_dashboard'),
    path('list/', views.transport_list, name='transport_list'),
    path('purchase-order/<int:po_id>/accept/', views.accept_purchase_order, name='accept_purchase_order'),
    path('purchase-order/<int:po_id>/complete/', views.complete_purchase_order, name='complete_purchase_order'),
    path('purchase-item/<int:item_id>/driver-confirm/',views.driver_confirm_purchase_item,name='driver_confirm_purchase_item'),
    path("driver/alert-results/",views.driver_alert_results,name="driver_alert_results"),
    path("purchase-order/<int:po_id>/complete/",views.complete_purchase_order,name="complete_purchase_order"),
]