from django.urls import path
from . import views

app_name = 'dining'

urlpatterns = [
    path('mesas/', views.table_map, name='table-map'),
    path('mesas/<int:pk>/open-modal/', views.table_open_modal, name='table-open-modal'),
    path('mesas/<int:pk>/open/', views.table_open, name='table-open'),
    path('mesas/<int:pk>/redirect/', views.table_redirect, name='table-redirect'),
]