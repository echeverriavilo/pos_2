from django.urls import path
from . import views
from .views import TerminalVentasView

app_name = 'orders'

urlpatterns = [
    path('', views.active_order, name='active-order'),
    path('nuevo/', views.new_order, name='new-order'),
    path('historial/', views.history, name='history'),
    path('terminal-ventas/', TerminalVentasView.as_view(), name='terminal-ventas'),
    path('terminal-ventas/products/', views.product_list_partial, name='product-list-partial'),
    path('terminal-ventas/add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('terminal-ventas/remove-from-cart/<int:order_item_id>/', views.remove_from_cart, name='remove-from-cart'),
]