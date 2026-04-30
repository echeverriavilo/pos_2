from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from apps.core.forms import RoleForm, UserForm
from apps.core.models import CustomUser, Role
from apps.core.services.auth import require_permission
from apps.core.services.role import RoleService, RoleServiceError


def home(request):
    return render(request, 'core/home.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña inválidos.')
            return render(request, 'core/login.html')
    else:
        return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def config(request):
    return render(request, 'core/config.html')


# ---------------------------------------------------------------------------
# Vistas CRUD de roles
# ---------------------------------------------------------------------------

@login_required
def role_list(request):
    """Lista los roles del tenant."""
    require_permission(request.user, 'manage_users')
    roles = Role.objects.for_tenant(request.tenant).filter(inhabilitado=False).order_by('-is_active', 'name')
    return render(request, 'core/role_list.html', {'roles': roles})


@login_required
def role_create(request):
    """Crea un nuevo rol para el tenant."""
    require_permission(request.user, 'manage_users')
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            try:
                RoleService.create_role(
                    tenant=request.tenant,
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data.get('description', ''),
                )
                messages.success(request, 'Rol creado exitosamente.')
                return redirect('core:role-list')
            except RoleServiceError as e:
                form.add_error(None, str(e))
    else:
        form = RoleForm()
    return render(request, 'core/role_form.html', {
        'form': form,
        'title': 'Crear Rol',
    })


@login_required
def role_edit(request, pk):
    """Edita un rol existente del tenant."""
    require_permission(request.user, 'manage_users')
    role = get_object_or_404(Role.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            try:
                RoleService.update_role(
                    role=role,
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data.get('description', ''),
                )
                messages.success(request, 'Rol actualizado exitosamente.')
                return redirect('core:role-list')
            except RoleServiceError as e:
                form.add_error(None, str(e))
    else:
        form = RoleForm(instance=role)
    return render(request, 'core/role_form.html', {
        'form': form,
        'title': 'Editar Rol',
    })


@login_required
def role_toggle_active(request, pk):
    """Pausa o reanuda un rol (desactivación temporal)."""
    require_permission(request.user, 'manage_users')
    role = get_object_or_404(Role.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk)
    if request.method != 'POST':
        return redirect('core:role-list')
    RoleService.toggle_active(role=role)
    estado = "pausado" if not role.is_active else "reactivado"
    messages.success(request, f'Rol {estado}.')
    return redirect('core:role-list')


@login_required
def role_inhabilitar(request, pk):
    """Inhabilita permanentemente un rol (no se puede reactivar)."""
    require_permission(request.user, 'manage_users')
    role = get_object_or_404(Role.objects.for_tenant(request.tenant), pk=pk)
    if request.method != 'POST':
        return redirect('core:role-list')
    role.inhabilitado = True
    role.is_active = False
    role.save(update_fields=['inhabilitado', 'is_active'])
    messages.success(request, 'Rol inhabilitado permanentemente.')
    return redirect('core:role-list')


# ---------------------------------------------------------------------------
# Vistas CRUD de usuarios del tenant
# ---------------------------------------------------------------------------

@login_required
def user_list(request):
    """Lista los usuarios del tenant."""
    require_permission(request.user, 'manage_users')
    users = CustomUser.objects.filter(
        membership__tenant=request.tenant,
        inhabilitado=False,
    ).select_related('membership__role').order_by('-pausado', 'first_name', 'email')
    return render(request, 'core/user_list.html', {'users': users})


@login_required
def user_create(request):
    """Crea un nuevo usuario para el tenant."""
    from apps.core.services.user import UserService

    require_permission(request.user, 'manage_users')
    if request.method == 'POST':
        form = UserForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if not password:
                form.add_error('password', 'La contraseña es obligatoria para crear un usuario.')
            else:
                try:
                    UserService.create_tenant_user(
                        email=form.cleaned_data['email'],
                        password=password,
                        tenant=request.tenant,
                        role=form.cleaned_data['role'],
                        first_name=form.cleaned_data.get('first_name', ''),
                        last_name=form.cleaned_data.get('last_name', ''),
                    )
                    messages.success(request, 'Usuario creado exitosamente.')
                    return redirect('core:user-list')
                except (ValueError, Exception) as e:
                    form.add_error(None, str(e))
    else:
        form = UserForm(tenant=request.tenant)
    return render(request, 'core/user_form.html', {
        'form': form,
        'title': 'Crear Usuario',
    })


@login_required
def user_edit(request, pk):
    """Edita un usuario del tenant y su membresía."""
    from apps.core.services.user import UserService

    require_permission(request.user, 'manage_users')
    user = get_object_or_404(
        CustomUser.objects.filter(membership__tenant=request.tenant, inhabilitado=False),
        pk=pk,
    )
    membership = user.membership
    if request.method == 'POST':
        form = UserForm(request.POST, tenant=request.tenant, instance=user)
        if form.is_valid():
            try:
                UserService.update_tenant_user(
                    user,
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data.get('first_name', ''),
                    last_name=form.cleaned_data.get('last_name', ''),
                    role=form.cleaned_data['role'],
                    password=form.cleaned_data.get('password') or None,
                )
                messages.success(request, 'Usuario actualizado exitosamente.')
                return redirect('core:user-list')
            except (ValueError, Exception) as e:
                form.add_error(None, str(e))
    else:
        initial = {}
        if membership and membership.role:
            initial['role'] = membership.role
        form = UserForm(tenant=request.tenant, instance=user, initial=initial)
    return render(request, 'core/user_form.html', {
        'form': form,
        'title': 'Editar Usuario',
    })


@login_required
def user_toggle_active(request, pk):
    """Pausa o reanuda un usuario (desactivación temporal)."""
    require_permission(request.user, 'manage_users')
    user = get_object_or_404(
        CustomUser.objects.filter(membership__tenant=request.tenant, inhabilitado=False),
        pk=pk,
    )
    if request.method != 'POST':
        return redirect('core:user-list')
    user.pausado = not user.pausado
    user.save(update_fields=['pausado'])
    estado = "pausado" if user.pausado else "reactivado"
    messages.success(request, f'Usuario {estado}.')
    return redirect('core:user-list')


@login_required
def user_inhabilitar(request, pk):
    """Inhabilita permanentemente un usuario (no puede volver a activarse)."""
    require_permission(request.user, 'manage_users')
    user = get_object_or_404(
        CustomUser.objects.filter(membership__tenant=request.tenant),
        pk=pk,
    )
    if request.method != 'POST':
        return redirect('core:user-list')
    user.inhabilitado = True
    user.is_active = False
    user.pausado = False
    user.save(update_fields=['inhabilitado', 'is_active', 'pausado'])
    messages.success(request, 'Usuario inhabilitado permanentemente.')
    return redirect('core:user-list')


@login_required
def role_select_modal(request):
    """Modal para seleccionar o crear roles desde formularios de usuario."""
    require_permission(request.user, 'manage_users')
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            try:
                RoleService.create_role(tenant=request.tenant, name=name, description=description)
                messages.success(request, f'Rol "{name}" creado.')
            except RoleServiceError as e:
                error = str(e)
        else:
            error = 'El nombre es obligatorio.'
    roles = Role.objects.for_tenant(request.tenant).filter(inhabilitado=False, is_active=True)
    return render(request, 'core/partials/role_select_modal.html', {
        'roles': roles,
        'error': error,
    })
