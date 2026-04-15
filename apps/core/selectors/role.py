from apps.core.models import Role, Tenant


def list_for_tenant(tenant: Tenant):
    """Lista todos los roles de un tenant.

    Parámetros:
    - tenant: tenant cuyos roles se listan.

    Retorna:
    - QuerySet de Role.
    """
    return Role.objects.filter(tenant=tenant)


def get_with_permissions(role: Role):
    """Obtiene un rol con sus permisos.

    Parámetros:
    - role: rol a obtener.

    Retorna:
    - Role con select_related de permisos.
    """
    return Role.objects.select_related('tenant').prefetch_related('permissions').get(pk=role.pk)


def get_by_name(tenant: Tenant, name: str):
    """Obtiene un rol por nombre dentro de un tenant.

    Parámetros:
    - tenant: tenant al que pertenece el rol.
    - name: nombre del rol.

    Retorna:
    - Role o None.
    """
    return Role.objects.filter(tenant=tenant, name=name).first()