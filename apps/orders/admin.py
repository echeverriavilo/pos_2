from django.contrib import admin
from .models import Order, OrderItem, Transaction, TransactionItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'tipo_flujo', 'estado', 'total_bruto', 'propina_monto')
    list_filter = ('estado', 'tenant', 'tipo_flujo')
    search_fields = ('id', 'tenant__slug')
    ordering = ('-id',)
    raw_id_fields = ('tenant', 'table')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'cantidad', 'precio_unitario_snapshot', 'estado')
    list_filter = ('estado',)
    search_fields = ('order__id', 'product__nombre')
    raw_id_fields = ('order', 'product')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'monto', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('id', 'order__id')
    ordering = ('-created_at',)
    raw_id_fields = ('order', 'tenant')


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'order_item')
    raw_id_fields = ('transaction', 'order_item')