# Execution Plan — Hito 5: Pagos

## Fase 1: Modelos

- Crear Transaction
- Crear TransactionItem
- Definir enums

---

## Fase 2: Selectors

- obtener transactions por order
- calcular total_pagado
- calcular total_pendiente

---

## Fase 3: Servicios

Implementar:

- register_transaction
- apply_payment_to_items
- update_order_payment_state

---

## Fase 4: Lógica de Pagos

Implementar:

### Validaciones

- monto <= pendiente
- consistencia tenant

### Tipo PRODUCTOS

- validar items no pagados
- marcar items como PAGADO

---

## Fase 5: Transiciones de Order

Implementar:

### Flujo MESA

- actualizar a:
  - PAGADO_PARCIAL
  - COMPLETADO

### Flujo RAPIDO

- PAGADO_PARCIAL
- CONFIRMADO (si total pagado)
- COMPLETADO

---

## Fase 6: Integraciones

### Mesas

- si Order → COMPLETADO:
  - mesa → DISPONIBLE

### Inventario

- en flujo RAPIDO:
  - CONFIRMADO → trigger de stock

---

## Fase 7: Invariantes

Validar:

- total_pagado nunca excede total_bruto
- OrderItem PAGADO no cambia
- COMPLETADO implica pago completo

---

## Fase 8: Testing

Tests obligatorios:

- pago total
- pago parcial
- pago por productos
- transición de estados
- bloqueo de items
- consistencia de totales

---

## Fase 9: Validación

- tests passing
- uso de transaction.atomic
- consistencia con invariants