# Atomicidad

## Regla General

Las operaciones críticas deben ejecutarse de forma atómica.

---

## Operaciones Críticas

### Confirmación de pedido (flujo rápido)

Debe ejecutarse como una sola transacción:

1. Validar pago completo
2. Cambiar estado a CONFIRMADO
3. Generar movimientos de stock

---

### Pago parcial por productos

1. Crear Transaction
2. Marcar OrderItem como PAGADO
3. Crear TransactionItem

---

### Anulación de producto

1. Marcar OrderItem como ANULADO
2. Generar reversa de stock
3. Recalcular total de Order

---

## Restricción

- Ninguna de estas operaciones puede quedar en estado parcial