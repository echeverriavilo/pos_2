from apps.orders.models import CashRegister


class CashRegisterSelector:
    @staticmethod
    def list_cash_registers(tenant):
        """Lista todas las cajas del tenant.

        Parámetros:
        - tenant: tenant de la operación.

        Retorno:
        - QuerySet de CashRegister filtrado por tenant.
        """
        return CashRegister.objects.for_tenant(tenant).all()

    @staticmethod
    def get_cash_register(tenant, pk):
        """Obtiene una caja por su id y tenant.

        Parámetros:
        - tenant: tenant de la operación.
        - pk: id de la caja.

        Retorno:
        - CashRegister o DoesNotExist.
        """
        return CashRegister.objects.for_tenant(tenant).get(pk=pk)