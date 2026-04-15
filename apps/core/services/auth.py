from django.core.exceptions import PermissionDenied

from apps.core.models.tenant import Tenant


class AuthorizationError(PermissionDenied):
    pass


def validate_tenant_access(user, tenant: Tenant) -> bool:
    """Valida que el usuario tenga acceso al tenant.

    Parámetros:
    - user: usuario que intenta acceder
    - tenant: tenant al que se intenta acceder

    Retorna:
    - True si el acceso es válido

    raises:
    - AuthorizationError si el acceso es denegado
    """
    if user.is_platform_staff:
        return True

    # Aseguramos que la membresía esté cargada o sea accesible
    membership = getattr(user, 'membership', None)

    if not membership:
        if user.is_superuser:
            return True  # Superusers sin membresía pueden acceder a cualquier tenant.
        else:
            raise AuthorizationError('El usuario no tiene una membresía asignada y por lo tanto no tiene acceso a un tenant.')

    user_tenant = membership.tenant
    if tenant is None:
        raise AuthorizationError('El tenant no es válido.')
    if user_tenant is None or user_tenant.id != tenant.id:
        raise AuthorizationError('Acceso denegado al tenant.')

    return True


def validate_role_permission(user, action: str) -> bool:
    """Valida que el rol del usuario permita la acción.

    Parámetros:
    - user: usuario que intenta realizar la acción
    - action: codename de la acción del sistema

    Retorna:
    - True si el permiso es válido

    raises:
    - AuthorizationError si el permiso es denegado
    """
    if user.is_superuser:
        return True

    if user.is_platform_staff:
        return True

    membership = getattr(user, 'membership', None)
    if not membership or not membership.role:
        raise AuthorizationError('El usuario no tiene un rol asignado.')

    if not membership.role.has_permission(action):
        raise AuthorizationError(f'Permiso denegado: {action}')

    return True


def require_tenant_access(user, tenant: Tenant) -> None:
    """Versión que lanza excepción para usar en servicios."""
    validate_tenant_access(user, tenant)


def require_permission(user, action: str) -> None:
    """Versión que lanza excepción para usar en servicios."""
    validate_role_permission(user, action)
