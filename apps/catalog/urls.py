from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('categorías/', views.category_list, name='category-list'),
]