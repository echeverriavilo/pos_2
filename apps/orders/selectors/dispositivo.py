from apps.orders.models.dispositivo import Dispositivo
from apps.orders.models.configuracion_dispositivo import ConfiguracionDispositivo


class DispositivoSelector:
    @classmethod
    def get_for_tenant_and_name(cls, tenant, nombre):
        return Dispositivo.objects.for_tenant(tenant).filter(nombre=nombre).first()

    @classmethod
    def get_activos_for_tenant(cls, tenant):
        return Dispositivo.objects.for_tenant(tenant).filter(activo=True).order_by('nombre')


class ConfiguracionDispositivoSelector:
    @classmethod
    def get_configurations_for_product(cls, tenant, producto):
        return ConfiguracionDispositivo.objects.for_tenant(tenant).filter(
            producto=producto
        ).order_by('-prioridad')

    @classmethod
    def get_configurations_for_category(cls, tenant, categoria):
        return ConfiguracionDispositivo.objects.for_tenant(tenant).filter(
            categoria=categoria
        ).order_by('-prioridad')

    @classmethod
    def get_effective_configuration_for_product(cls, tenant, producto):
        config = cls.get_configurations_for_product(tenant, producto).first()
        if config:
            return config

        # Use 'category' (English) not 'categoria'
        config = cls.get_configurations_for_category(tenant, producto.category).first()
        if config:
            return config

        return None