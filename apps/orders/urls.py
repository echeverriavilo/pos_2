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
    path('terminal-ventas/modal-pago/', views.terminal_modal_pago, name='terminal-modal-pago'),
    path('mesa/<int:table_id>/', views.mesa_pedido, name='mesa-pedido'),
    path('mesa/<int:table_id>/confirmar/', views.mesa_confirmar_pedido, name='mesa-confirmar'),
    path('mesa/<int:table_id>/solicitar-cuenta/', views.mesa_solicitar_cuenta, name='mesa-solicitar-cuenta'),
    path('mesa/<int:table_id>/modal-pago/', views.mesa_modal_pago, name='mesa-modal-pago'),
    path('mesa/<int:table_id>/liberar/', views.mesa_liberar_mesa, name='mesa-liberar'),
    path('orden/<int:order_id>/fijar-propina/', views.orden_fijar_propina, name='orden-fijar-propina'),
    path('orden/<int:order_id>/procesar-pago/', views.orden_procesar_pago, name='orden-procesar-pago'),
    path('orden/<int:order_id>/pre-cuenta/', views.orden_pre_cuenta, name='orden-pre-cuenta'),
]