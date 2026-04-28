# Acceptance Criteria — Hito 4: Órdenes

## Objetivo

Implementar la gestión de órdenes y sus ítems, incluyendo estados, flujos y consistencia con reglas de negocio.

---

## Creación de Order

Se puede crear un Order con:

- tenant
- tipo_flujo: MESA | RAPIDO
- table (nullable)

### Reglas

- Si tipo_flujo = MESA:
  - debe tener table
- Si tipo_flujo = RAPIDO:
  - table debe ser null

- estado inicial = ABIERTO

---

## Estados de Order

Estados válidos:

- ABIERTO
- CONFIRMADO
- PAGADO_PARCIAL
- COMPLETADO
- ANULADO

---

## Transiciones válidas

### Flujo MESA

- ABIERTO → PAGADO_PARCIAL
- ABIERTO → COMPLETADO
- PAGADO_PARCIAL → COMPLETADO

---

### Flujo RAPIDO

- ABIERTO → PAGADO_PARCIAL
- PAGADO_PARCIAL → CONFIRMADO (solo si pago total)
- CONFIRMADO → COMPLETADO

---

## Creación de OrderItem

Se pueden agregar productos a una orden:

- cantidad > 0
- precio_unitario_snapshot tomado desde Product

---

## Estados de OrderItem

- PENDIENTE
- PREPARACION
- ENTREGADO
- ANULADO
- PAGADO

---

## Envío a preparación

### Flujo MESA

- Al agregar un producto:
  - estado → PREPARACION

### Flujo RAPIDO

- Al agregar producto:
  - estado → PENDIENTE

- Solo después de pago total:
  - estado → PREPARACION

---

## Restricciones

- No se pueden modificar items en estado PAGADO
- No se pueden anular items PAGADO

---

## Totales

- total_bruto = suma de:
  - cantidad * precio_unitario_snapshot

---

## Integración con Mesas

- Order tipo MESA:
  - debe estar asociado a una DiningTable
  - debe ser consistente con estado de mesa

---

## Multitenancy

- Todas las operaciones requieren tenant
- Order y OrderItem deben pertenecer al mismo tenant

---

## Consistencia

Debe cumplirse:

- No puede existir CONFIRMADO en flujo rápido sin pago total
- Order COMPLETADO implica:
  - total pagado >= total_bruto