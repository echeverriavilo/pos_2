from typing import List
from django.db import transaction

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.orders.models import Comanda, ComandaItem, OrderItem
from apps.orders.selectors import DispositivoSelector, ConfiguracionDispositivoSelector
from apps.orders.services.dispositivo import DispositivoService


class ComandaError(Exception):
    pass


class ComandaService:
    @classmethod
    def generar_comandas_para_order_item(cls, *, user, order_item: OrderItem) -> List[Comanda]:
        """Genera comandas para un OrderItem según la configuración de dispositivos."""
        validate_tenant_access(user, order_item.order.tenant)
        validate_role_permission(user, SystemActions.ADD_ITEM)

        tenant = order_item.order.tenant
        product = order_item.product

        config = ConfiguracionDispositivoSelector.get_effective_configuration_for_product(tenant, product)
        if config:
            dispositivos = [config.dispositivo]
        else:
            default_dispositivo = DispositivoService.get_default_for_tenant(tenant)
            if not default_dispositivo:
                raise ComandaError(f"No se encontró dispositivo predeterminado para el tenant {tenant.id}")
            dispositivos = [default_dispositivo]

        comandas_creadas = []
        with transaction.atomic():
            for dispositivo in dispositivos:
                comanda = Comanda.objects.for_tenant(tenant).filter(
                    orden=order_item.order,
                    dispositivo=dispositivo,
                    estado__in=[Comanda.Estado.PENDIENTE, Comanda.Estado.LISTA],
                ).first()

                if not comanda:
                    comanda = Comanda.objects.create(
                        tenant=tenant,
                        orden=order_item.order,
                        dispositivo=dispositivo,
                        estado=Comanda.Estado.PENDIENTE,
                    )

                if not ComandaItem.objects.filter(comanda=comanda, order_item=order_item).exists():
                    ComandaItem.objects.create(
                        comanda=comanda,
                        order_item=order_item,
                    )
                comandas_creadas.append(comanda)

        return comandas_creadas

    @classmethod
    def actualizar_estado_comanda(cls, *, user, comanda: Comanda, estado: str) -> Comanda:
        """Actualiza el estado de una comanda validando la transición permitida."""
        validate_tenant_access(user, comanda.tenant)
        validate_role_permission(user, SystemActions.MANAGE_TABLES)

        current_state = comanda.estado
        if estado == current_state:
            raise ComandaError(f'La comanda ya está en el estado {estado}')

        allowed_transitions = {
            Comanda.Estado.PENDIENTE: [Comanda.Estado.LISTA, Comanda.Estado.CANCELADO],
            Comanda.Estado.LISTA: [Comanda.Estado.ENTREGADO, Comanda.Estado.CANCELADO],
            Comanda.Estado.ENTREGADO: [],
            Comanda.Estado.CANCELADO: [],
        }

        if estado not in allowed_transitions.get(current_state, []):
            raise ComandaError(f'Transición de estado no permitida: {current_state} → {estado}')

        with transaction.atomic():
            comanda.estado = estado
            comanda.save(update_fields=['estado'])

        return comanda