from django.db import transaction

from apps.dining.models import DiningTable
from apps.dining.selectors import DiningTableSelector
from apps.orders.services import OrderError, create_order_for_table


class DiningTableError(Exception):
    pass


class DiningTableService:
    @classmethod
    def create_table(cls, *, tenant, numero):
        return DiningTable.objects.create(tenant=tenant, numero=numero)

    @classmethod
    def open_table(cls, *, table):
        if table.estado != DiningTable.States.DISPONIBLE:
            raise DiningTableError('Solo se puede abrir una mesa DISPONIBLE.')
        if DiningTableSelector.get_active_order_for_table(table):
            raise DiningTableError('Ya existe un order activo para la mesa.')

        with transaction.atomic():
            try:
                order = create_order_for_table(table=table)
            except OrderError as exc:
                raise DiningTableError(str(exc)) from exc
            table.estado = DiningTable.States.OCUPADA
            table.save(update_fields=['estado'])
            return order

    @classmethod
    def set_table_paying(cls, *, table):
        if table.estado != DiningTable.States.OCUPADA:
            raise DiningTableError('Solo una mesa OCUPADA puede pasar a PAGANDO.')
        if not DiningTableSelector.get_active_order_for_table(table):
            raise DiningTableError('La mesa debe tener un order activo antes de pagar.')
        with transaction.atomic():
            table.estado = DiningTable.States.PAGANDO
            table.save(update_fields=['estado'])
            return table

    @classmethod
    def reopen_table(cls, *, table):
        if table.estado != DiningTable.States.PAGANDO:
            raise DiningTableError('Solo una mesa PAGANDO puede reabrirse.')
        if not DiningTableSelector.get_active_order_for_table(table):
            raise DiningTableError('La mesa debe tener un order activo para reabrirla.')
        with transaction.atomic():
            table.estado = DiningTable.States.OCUPADA
            table.save(update_fields=['estado'])
            return table
