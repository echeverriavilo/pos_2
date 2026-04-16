from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.orders.models import Dispositivo


class DispositivoError(PermissionDenied):
    pass


class DispositivoService:
    @classmethod
    def create_dispositivo(cls, *, user, tenant, nombre, tipo, activo=True):
        """Crea un nuevo dispositivo de salida para un tenant."""
        validate_tenant_access(user, tenant)
        validate_role_permission(user, SystemActions.MANAGE_DEVICES)
        with transaction.atomic():
            dispositivo = Dispositivo.objects.create(
                tenant=tenant,
                nombre=nombre,
                tipo=tipo,
                activo=activo,
            )
            return dispositivo

    @classmethod
    def update_dispositivo(cls, *, user, dispositivo, nombre=None, tipo=None, activo=None):
        """Actualiza un dispositivo existente."""
        validate_tenant_access(user, dispositivo.tenant)
        validate_role_permission(user, SystemActions.MANAGE_DEVICES)
        with transaction.atomic():
            if nombre is not None:
                dispositivo.nombre = nombre
            if tipo is not None:
                dispositivo.tipo = tipo
            if activo is not None:
                dispositivo.activo = activo
            fields_to_update = [f for f, v in [('nombre', nombre), ('tipo', tipo), ('activo', activo)] if v is not None]
            if fields_to_update:
                dispositivo.save(update_fields=fields_to_update)
            return dispositivo

    @classmethod
    def delete_dispositivo(cls, *, user, dispositivo):
        """Elimina un dispositivo (borrado lógico)."""
        cls.update_dispositivo(user=user, dispositivo=dispositivo, activo=False)

    @classmethod
    def get_activos_for_tenant(cls, tenant):
        """Obtiene todos los dispositivos activos de un tenant."""
        return Dispositivo.objects.for_tenant(tenant).filter(activo=True)

    @classmethod
    def get_by_name_and_tenant(cls, *, tenant, nombre):
        """Obtiene un dispositivo por nombre y tenant."""
        return Dispositivo.objects.for_tenant(tenant).filter(nombre=nombre).first()

    @classmethod
    def get_default_for_tenant(cls, tenant):
        """Obtiene el dispositivo predeterminado para un tenant.
        Por definición, es el primero activo ordenado por nombre.
        """
        return Dispositivo.objects.for_tenant(tenant).filter(activo=True).order_by('nombre').first()