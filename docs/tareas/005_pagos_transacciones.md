# 005 - Pagos y transacciones

## Objetivo

Implementar pagos sobre `Order` con transacciones totales, abonos y pagos por productos.

## Contexto

La tarea agrega trazabilidad de pagos y actualiza el estado de la orden segun el saldo acumulado.

## Dependencias

- `004_motor_ordenes_y_items.md`

## Reglas aplicables

- una orden puede tener multiples transacciones;
- el total pagado no puede exceder el total de la cuenta;
- pagos por productos solo aplican a items no pagados;
- no dejar estados parciales en una operacion de pago.

## Plan de implementacion

- crear `Transaction` y `TransactionItem`;
- implementar selectores de totales pagado y pendiente;
- crear `register_transaction`, `apply_payment_to_items` y `update_order_payment_state`;
- cubrir pago total, parcial por monto y parcial por productos.

## Criterios de aceptacion

- se puede registrar una transaccion valida;
- el saldo pendiente se recalcula correctamente;
- los items pagados quedan trazados por transaccion;
- el estado de la orden cambia segun el monto acumulado;
- existen tests para los tres tipos de pago.

## Validacion requerida

- `pytest apps/orders/tests`

## Estado

Completado

## Notas y resultados

- el modulo de pagos quedo integrado con los estados de orden;
- la trazabilidad de items pagados vive en `TransactionItem`.
