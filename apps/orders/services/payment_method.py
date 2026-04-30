from django.db import transaction

from apps.orders.models import PaymentMethod


class PaymentMethodServiceError(Exception):
    pass


class PaymentMethodService:
    @staticmethod
    def create_payment_method(*, tenant, nombre: str, orden: int = 0, activo: bool = True) -> PaymentMethod:
        """Crea un nuevo método de pago para el tenant."""
        if not nombre:
            raise PaymentMethodServiceError('El nombre es obligatorio.')
        with transaction.atomic():
            return PaymentMethod.objects.create(
                tenant=tenant, nombre=nombre, orden=orden, activo=activo,
            )

    @staticmethod
    def update_payment_method(*, payment_method: PaymentMethod, nombre: str = None, orden: int = None) -> PaymentMethod:
        """Actualiza un método de pago existente."""
        updated_fields = []
        if nombre is not None:
            if not nombre:
                raise PaymentMethodServiceError('El nombre es obligatorio.')
            payment_method.nombre = nombre
            updated_fields.append('nombre')
        if orden is not None:
            payment_method.orden = orden
            updated_fields.append('orden')
        if updated_fields:
            payment_method.save(update_fields=updated_fields)
        return payment_method

    @staticmethod
    def toggle_active(*, payment_method: PaymentMethod) -> PaymentMethod:
        """Activa o desactiva un método de pago."""
        payment_method.activo = not payment_method.activo
        payment_method.save(update_fields=['activo'])
        return payment_method
