# Acceptance Criteria — Hito 5: Pagos

## Objetivo

Implementar el sistema de pagos sobre Order, soportando:

- pagos totales
- pagos parciales
- pagos por productos

Garantizando consistencia con reglas de negocio e invariantes.

---

## Creación de Transaction

Se puede registrar una Transaction con:

- tenant
- order
- monto
- tipo_pago:
  - TOTAL
  - ABONO
  - PRODUCTOS

---

## Reglas Generales

- Un Order puede tener múltiples Transaction
- El total pagado:
  - NO puede exceder total_bruto

---

## Tipos de Pago

### Pago TOTAL

- monto = total pendiente
- puede cerrar la orden directamente

---

### Pago ABONO

- monto arbitrario
- no modifica OrderItem
- afecta total pendiente

---

### Pago por PRODUCTOS

- debe asociarse a uno o más OrderItem vía TransactionItem

Restricciones:

- solo items no pagados
- los items pasan a estado PAGADO

---

## Estados de Order

### Transiciones por pagos

#### Flujo MESA

- ABIERTO → PAGADO_PARCIAL
- ABIERTO → COMPLETADO (si pago total)
- PAGADO_PARCIAL → COMPLETADO

---

#### Flujo RAPIDO

- ABIERTO → PAGADO_PARCIAL
- PAGADO_PARCIAL → CONFIRMADO (solo si total pagado)
- CONFIRMADO → COMPLETADO

---

## Bloqueo de Items

- Un OrderItem en estado PAGADO:
  - no puede ser modificado
  - no puede ser anulado

---

## Consistencia de Totales

Debe cumplirse:

- total_pagado ≤ total_bruto
- Order COMPLETADO ⇔ total_pagado ≥ total_bruto

---

## Integración con Inventario

### Flujo MESA

- ya descontado al agregar producto (no afecta pagos)

### Flujo RAPIDO

- al pasar a CONFIRMADO:
  - debe dispararse descuento de stock

---

## Integración con Mesas

- Si Order pasa a COMPLETADO:
  - DiningTable → DISPONIBLE

---

## Multitenancy

- Transaction debe pertenecer al mismo tenant que Order