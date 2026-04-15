from django.contrib import admin
from .models import DiningTable


@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tenant', 'estado')
    list_filter = ('tenant', 'estado')
    search_fields = ('numero',)
    ordering = ('tenant', 'numero')