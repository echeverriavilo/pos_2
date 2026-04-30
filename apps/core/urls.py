from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('config/', views.config, name='config'),
    path('roles/', views.role_list, name='role-list'),
    path('roles/crear/', views.role_create, name='role-create'),
    path('roles/<int:pk>/editar/', views.role_edit, name='role-edit'),
    path('roles/<int:pk>/pausar/', views.role_toggle_active, name='role-toggle'),
    path('roles/<int:pk>/inhabilitar/', views.role_inhabilitar, name='role-inhabilitar'),
    path('usuarios/', views.user_list, name='user-list'),
    path('usuarios/crear/', views.user_create, name='user-create'),
    path('usuarios/<uuid:pk>/editar/', views.user_edit, name='user-edit'),
    path('usuarios/<uuid:pk>/pausar/', views.user_toggle_active, name='user-toggle'),
    path('usuarios/<uuid:pk>/inhabilitar/', views.user_inhabilitar, name='user-inhabilitar'),
    path('roles/modal/', views.role_select_modal, name='role-select-modal'),
]
