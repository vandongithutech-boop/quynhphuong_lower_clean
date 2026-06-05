from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("create/", views.order_create, name="order_create"),

    path("api/customers/", views.api_customers, name="api_customers"),
    path("api/flowers/", views.api_flowers, name="api_flowers"),
    path("api/stock/", views.api_product_stock, name="api_product_stock"),
    path("api/raw-stock/", views.api_raw_stock_warning, name="api_raw_stock_warning"),
]