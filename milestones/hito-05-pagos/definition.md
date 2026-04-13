# Definition — Hito 5: Pagos

## Entidades

### Transaction

- tenant: FK(Tenant)
- order: FK(Order)
- monto: decimal
- tipo_pago: enum (TOTAL, ABONO, PRODUCTOS)

---

### TransactionItem

- transaction: FK(Transaction)
- order_item: FK(OrderItem)

---

## Conceptos Derivados

### total_pagado(Order)

- suma de Transaction.monto

---

### total_pendiente(Order)

- total_bruto - total_pagado

---

## Operaciones de Dominio

### register_transaction

- crea Transaction
- valida reglas de monto
- actualiza estado de Order

---

### apply_payment_to_items

- para tipo PRODUCTOS:
  - asigna TransactionItem
  - marca OrderItem como PAGADO

---

### update_order_payment_state

- evalúa total_pagado vs total_bruto
- ejecuta transición de estado

---

## Reglas de Negocio

- monto nunca puede exceder pendiente
- OrderItem PAGADO es inmutable

---

## Dependencias

- Order
- OrderItem
- DiningTable
- StockMovement (solo trigger, no implementación completa)