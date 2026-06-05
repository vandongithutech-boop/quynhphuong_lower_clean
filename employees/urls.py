from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('them/', views.employee_create, name='employee_create'),
    path('sua/<int:pk>/', views.employee_update, name='employee_update'),
    path('xoa/<int:pk>/', views.employee_delete, name='employee_delete'),
]