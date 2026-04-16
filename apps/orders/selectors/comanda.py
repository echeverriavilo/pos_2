from apps.orders.models import Comanda, ComandaItem


class ComandaSelector:
    @classmethod
    def get_pendientes_por_dispositivo(cls, dispositivo):
        return Comanda.objects.for_tenant(dispositivo.tenant).filter(
            dispositivo=dispositivo,
            estado=Comanda.Estado.PENDIENTE,
        ).order_by('creado_en')

    @classmethod
    def get_por_orden(cls, orden):
        return Comanda.objects.for_tenant(orden.tenant).filter(
            orden=orden
        ).order_by('-creado_en')

    @classmethod
    def get_con_items(cls, comanda_id):
        return Comanda.objects.select_related('dispositivo', 'orden').prefetch_related(
            'items__order_item__product'
        ).filter(pk=comanda_id).first()

    @classmethod
    def get_activas_por_dispositivo(cls, dispositivo):
        return Comanda.objects.for_tenant(dispositivo.tenant).filter(
            dispositivo=dispositivo,
            estado__in=[Comanda.Estado.PENDIENTE, Comanda.Estado.LISTA],
        ).order_by('creado_en')