from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.active_order, name='active-order'),
    path('nuevo/', views.new_order, name='new-order'),
    path('historial/', views.history, name='history'),
]