"""
URL configuration for grastro project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalogo/', include('apps.catalog.urls')),
    path('salon/', include('apps.dining.urls')),
    path('ordenes/', include('apps.orders.urls')),
    path('', include('apps.core.urls')),
]