from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('flowers/', views.flower_list, name='flower_list'),
    path('flowers/create/', views.flower_create, name='flower_create'),
    path('flowers/<int:pk>/edit/', views.flower_update, name='flower_update'),
    path('flowers/<int:pk>/delete/', views.flower_delete, name='flower_delete'),

    path('khach-hang/', views.customer_list, name='customer_list'),
    path('khach-hang/them/', views.customer_create, name='customer_create'),
    path('khach-hang/sua/<int:pk>/', views.customer_update, name='customer_update'),
    path('khach-hang/xoa/<int:pk>/', views.customer_delete, name='customer_delete'),
]