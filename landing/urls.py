from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/agendar/', views.agendar_cita, name='agendar_cita'),
    path('checkout/', views.checkout, name='checkout'),
]

