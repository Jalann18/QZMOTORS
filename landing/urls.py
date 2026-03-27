from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/agendar/', views.agendar_cita, name='agendar_cita'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.checkout_process, name='checkout_process'),
    path('checkout/return/', views.checkout_return, name='checkout_return'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
]

