from django.db.models import Case, F, Sum, When

from apps.orders.models import CashMovement, CashSession


class CashSessionSelector:
    @staticmethod
    def get_active_session_for_register(tenant, cash_register):
        """Obtiene la sesión abierta para una caja, si existe.

        Parámetros:
        - tenant: tenant de la operación.
        - cash_register: CashRegister a consultar.

        Retorno:
        - CashSession ABIERTA o None.
        """
        return CashSession.objects.for_tenant(tenant).filter(
            cash_register=cash_register,
            estado=CashSession.States.ABIERTA,
        ).first()

    @staticmethod
    def get_active_session_for_tenant(tenant):
        """Obtiene cualquiera sesión abierta del tenant (para flujo de pagos).

        Parámetros:
        - tenant: tenant de la operación.

        Retorno:
        - CashSession ABIERTA o None.
        """
        return CashSession.objects.for_tenant(tenant).filter(
            estado=CashSession.States.ABIERTA,
        ).first()

    @staticmethod
    def get_active_session_for_order(tenant, order):
        """Obtiene la sesión de caja abierta compatible con el flujo de la orden.

        Parámetros:
        - tenant: tenant de la operación.
        - order: orden a verificar.

        Retorno:
        - CashSession ABIERTA compatible con el flujo de la orden, o None.
        """
        from apps.orders.models import Order

        if order.tipo_flujo == Order.Flow.MESA:
            compatible_registers = tenant.cash_registers.filter(
                soporta_flujo_mesa=True,
                activo=True,
            )
        else:
            compatible_registers = tenant.cash_registers.filter(
                soporta_flujo_rapido=True,
                activo=True,
            )

        for cash_register in compatible_registers:
            session = CashSessionSelector.get_active_session_for_register(tenant, cash_register)
            if session:
                return session
        return None

    @staticmethod
    def get_session_payment_breakdown(session):
        """Calcula el desglose neto por medio de pago de todos los movimientos de la sesión.

        INGRESOs y AJUSTEs suman, EGRESOs restan. Agrupa por payment_method
        del CashMovement (incluye movimientos automáticos y manuales).

        Parámetros:
        - session: CashSession a consultar.

        Retorno:
        - dict {payment_method_id: total_sistema}
        """
        breakdown = CashMovement.objects.filter(
            cash_session=session,
            payment_method__isnull=False,
        ).values('payment_method').annotate(
            total_sistema=Sum(
                Case(
                    When(tipo=CashMovement.MovementType.EGRESO, then=-F('monto')),
                    default=F('monto'),
                )
            )
        )
        return {item['payment_method']: item['total_sistema'] for item in breakdown}

    @staticmethod
    def list_session_movements(session):
        """Lista los movimientos de una sesión de caja.

        Parámetros:
        - session: CashSession a consultar.

        Retorno:
        - QuerySet de CashMovement de la sesión.
        """
        return CashMovement.objects.filter(cash_session=session).order_by('created_at')