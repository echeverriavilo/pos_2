from django.urls import path
from . import views
from .views_cash import (
    caja_lista,
    caja_crear,
    caja_editar,
    caja_toggle_activa,
    sesion_abrir,
    sesion_detalle,
    sesion_cerrar,
    sesion_confirmar,
    sesion_movimiento,
    sesiones_cerradas,
)
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
    path('orden/<int:order_id>/procesar-pago/', views.orden_procesar_pago, name='orden-procesar-pago'),
    path('orden/<int:order_id>/pre-cuenta/', views.orden_pre_cuenta, name='orden-pre-cuenta'),
    path('caja/', caja_lista, name='caja-lista'),
    path('caja/crear/', caja_crear, name='caja-crear'),
    path('caja/<int:pk>/editar/', caja_editar, name='caja-editar'),
    path('caja/<int:pk>/toggle/', caja_toggle_activa, name='caja-toggle-activa'),
    path('caja/sesion/abrir/', sesion_abrir, name='sesion-abrir'),
    path('caja/sesion/<int:session_id>/', sesion_detalle, name='sesion-detalle'),
    path('caja/sesion/<int:session_id>/cerrar/', sesion_cerrar, name='sesion-cerrar'),
    path('caja/sesion/<int:session_id>/confirmar/', sesion_confirmar, name='sesion-confirmar'),
    path('caja/sesion/<int:session_id>/movimiento/', sesion_movimiento, name='sesion-movimiento'),
    path('caja/cierres/', sesiones_cerradas, name='sesiones-cerradas'),
]