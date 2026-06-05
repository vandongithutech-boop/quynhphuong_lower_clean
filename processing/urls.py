from django.urls import path
from . import views

urlpatterns = [
    path('', views.processing_list, name='processing_list'),
    path('create/', views.create_processing_ticket, name='create_processing_ticket'),
    path('api/available-loose-stems/', views.get_available_loose_stems, name='get_available_loose_stems'),
    path('manual-create/',views.create_manual_processing_ticket,name='create_manual_processing_ticket'
),
]