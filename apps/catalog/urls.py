from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('crear/', views.product_create, name='product-create'),
    path('<int:pk>/editar/', views.product_edit, name='product-edit'),
    path('<int:pk>/pausar/', views.product_toggle_active, name='product-toggle'),
    path('<int:pk>/inhabilitar/', views.product_inhabilitar, name='product-inhabilitar'),
    path('categorias/', views.category_list, name='category-list'),
    path('categorias/crear/', views.category_create, name='category-create'),
    path('categorias/<int:pk>/editar/', views.category_edit, name='category-edit'),
    path('categorias/<int:pk>/pausar/', views.category_toggle_active, name='category-toggle'),
    path('categorias/<int:pk>/inhabilitar/', views.category_inhabilitar, name='category-inhabilitar'),
    path('categorias/modal/', views.category_select_modal, name='category-select-modal'),
]
