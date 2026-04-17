from django.db import transaction

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.dining.models import DiningTable
from apps.dining.selectors import DiningTableSelector
from apps.orders.services import OrderError, create_order_for_table


class DiningTableError(Exception):
    pass


class DiningTableService:
    @classmethod
    def create_table(cls, *, user, tenant, numero):
        validate_tenant_access(user, tenant)
        validate_role_permission(user, SystemActions.MANAGE_TABLES)
        return DiningTable.objects.create(tenant=tenant, numero=numero)

    @classmethod
    def open_table(cls, *, user, table):
        validate_tenant_access(user, table.tenant)
        validate_role_permission(user, SystemActions.MANAGE_TABLES)
        if table.estado != DiningTable.States.DISPONIBLE:
            raise DiningTableError('Solo se puede abrir una mesa DISPONIBLE.')
        if DiningTableSelector.get_active_order_for_table(table):
            raise DiningTableError('Ya existe un order activo para la mesa.')

        with transaction.atomic():
            try:
                order = create_order_for_table(user=user, table=table)
            except OrderError as exc:
                raise DiningTableError(str(exc)) from exc
            table.estado = DiningTable.States.OCUPADA
            table.save(update_fields=['estado'])
            return order

    @classmethod
    def set_table_paying(cls, *, user, table):
        validate_tenant_access(user, table.tenant)
        validate_role_permission(user, SystemActions.MANAGE_TABLES)
        if table.estado != DiningTable.States.OCUPADA:
            raise DiningTableError('Solo una mesa OCUPADA puede pasar a PAGANDO.')
        if not DiningTableSelector.get_active_order_for_table(table):
            raise DiningTableError('La mesa debe tener un order activo antes de pagar.')
        with transaction.atomic():
            table.estado = DiningTable.States.PAGANDO
            table.save(update_fields=['estado'])
            return table

    @classmethod
    def reopen_table(cls, *, user, table):
        validate_tenant_access(user, table.tenant)
        validate_role_permission(user, SystemActions.MANAGE_TABLES)
        if table.estado != DiningTable.States.PAGANDO:
            raise DiningTableError('Solo una mesa PAGANDO puede reabrirse.')
        if not DiningTableSelector.get_active_order_for_table(table):
            raise DiningTableError('La mesa debe tener un order activo para reabrirla.')
        with transaction.atomic():
            table.estado = DiningTable.States.OCUPADA
            table.save(update_fields=['estado'])
            return table

    @classmethod
    def release_table(cls, *, user, table):
        """Cierra una mesa OCUPADA o PAGANDO sin movimientos activos.

        Si la mesa tiene una orden sin ítems activos (todos anulados o vacía),
        anula la orden y libera la mesa a DISPONIBLE.
        """
        validate_tenant_access(user, table.tenant)
        validate_role_permission(user, SystemActions.MANAGE_TABLES)
        if table.estado not in {DiningTable.States.OCUPADA, DiningTable.States.PAGANDO}:
            raise DiningTableError('Solo se puede liberar una mesa OCUPADA o PAGANDO.')

        order = DiningTableSelector.get_active_order_for_table(table)
        if not order:
            with transaction.atomic():
                table.estado = DiningTable.States.DISPONIBLE
                table.save(update_fields=['estado'])
                return table

        # Verificar que no tenga ítems activos (no anulados)
        has_active_items = order.items.exclude(estado='ANULADO').exists()
        if has_active_items:
            raise DiningTableError('No se puede liberar una mesa con pedidos activos. Anula los pedidos primero.')

        with transaction.atomic():
            from apps.orders.services.order import transition_order_state
            transition_order_state(user=user, order=order, target_state=order.States.ANULADO)
            table.estado = DiningTable.States.DISPONIBLE
            table.save(update_fields=['estado'])
            return table
