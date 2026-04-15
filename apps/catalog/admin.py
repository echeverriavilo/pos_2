from django.contrib import admin
from .models import Category, Product, Ingredient, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('nombre',)
    ordering = ('tenant', 'nombre')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'category', 'precio_bruto', 'stock_actual', 'es_inventariable')
    list_filter = ('category', 'es_inventariable')
    search_fields = ('nombre', 'category__nombre')
    ordering = ('category', 'nombre')
    raw_id_fields = ('tenant', 'category')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('nombre',)
    ordering = ('nombre',)
    raw_id_fields = ('tenant',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'tipo', 'cantidad', 'created_at')
    list_filter = ('tipo',)
    search_fields = ('product__nombre',)
    ordering = ('-created_at',)
    raw_id_fields = ('product',)