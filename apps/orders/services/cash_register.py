from decimal import Decimal

from django.db import transaction

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.orders.models import CashRegister


class CashRegisterError(Exception):
    pass


def create_cash_register(*, user, tenant, nombre, soporta_flujo_mesa=True, soporta_flujo_rapido=True):
    """Crea una nueva caja para el tenant.

    Parámetros:
    - user: usuario que ejecuta la operación.
    - tenant: tenant de la operación.
    - nombre: nombre de la caja.
    - soporta_flujo_mesa: si la caja soporta flujo con mesa.
    - soporta_flujo_rapido: si la caja soporta flujo rápido.

    Retorno:
    - CashRegister creada.
    """
    validate_tenant_access(user, tenant)
    validate_role_permission(user, SystemActions.MANAGE_CASH_REGISTERS)

    if not nombre or not nombre.strip():
        raise CashRegisterError('El nombre de la caja es obligatorio.')

    if not soporta_flujo_mesa and not soporta_flujo_rapido:
        raise CashRegisterError('La caja debe soportar al menos un flujo de venta.')

    return CashRegister.objects.create(
        tenant=tenant,
        nombre=nombre.strip(),
        soporta_flujo_mesa=soporta_flujo_mesa,
        soporta_flujo_rapido=soporta_flujo_rapido,
    )


def update_cash_register(*, user, tenant, pk, nombre=None, soporta_flujo_mesa=None, soporta_flujo_rapido=None):
    """Actualiza los datos de una caja existente.

    Parámetros:
    - user: usuario que ejecuta la operación.
    - tenant: tenant de la operación.
    - pk: id de la caja.
    - nombre: nuevo nombre (opcional).
    - soporta_flujo_mesa: nuevo valor (opcional).
    - soporta_flujo_rapido: nuevo valor (opcional).

    Retorno:
    - CashRegister actualizada.
    """
    validate_tenant_access(user, tenant)
    validate_role_permission(user, SystemActions.MANAGE_CASH_REGISTERS)

    cash_register = CashRegister.objects.for_tenant(tenant).get(pk=pk)

    if nombre is not None:
        cash_register.nombre = nombre.strip()
    if soporta_flujo_mesa is not None:
        cash_register.soporta_flujo_mesa = soporta_flujo_mesa
    if soporta_flujo_rapido is not None:
        cash_register.soporta_flujo_rapido = soporta_flujo_rapido

    if not cash_register.soporta_flujo_mesa and not cash_register.soporta_flujo_rapido:
        raise CashRegisterError('La caja debe soportar al menos un flujo de venta.')

    from apps.orders.selectors.cash_session import CashSessionSelector
    active_session = CashSessionSelector.get_active_session_for_register(tenant, cash_register)
    if active_session:
        import logging
        logger = logging.getLogger(__name__)
        # Allow updating name even with active session, but block flow changes
        if soporta_flujo_mesa is not None or soporta_flujo_rapido is not None:
            raise CashRegisterError('No se puede modificar los flujos soportados de una caja con sesión abierta.')

    cash_register.save()
    return cash_register


def toggle_cash_register(*, user, tenant, pk, activo):
    """Activa o desactiva una caja.

    Parámetros:
    - user: usuario que ejecuta la operación.
    - tenant: tenant de la operación.
    - pk: id de la caja.
    - activo: nuevo estado de activación.

    Retorno:
    - CashRegister actualizada.
    """
    validate_tenant_access(user, tenant)
    validate_role_permission(user, SystemActions.MANAGE_CASH_REGISTERS)

    cash_register = CashRegister.objects.for_tenant(tenant).get(pk=pk)

    if not activo:
        from apps.orders.selectors.cash_session import CashSessionSelector
        active_session = CashSessionSelector.get_active_session_for_register(tenant, cash_register)
        if active_session:
            raise CashRegisterError('No se puede desactivar una caja con sesión abierta.')

    cash_register.activo = activo
    cash_register.save(update_fields=['activo'])
    return cash_register