from django.urls import path
from . import views

app_name = 'dining'

urlpatterns = [
    path('mesas/', views.table_map, name='table-map'),
]