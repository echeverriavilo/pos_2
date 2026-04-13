# Execution Plan — Hito 4: Órdenes

## Fase 1: Modelos

- Crear modelo Order
- Crear modelo OrderItem
- Definir enums de estado

---

## Fase 2: Selectors

- obtener órdenes por tenant
- obtener orden activa por mesa
- obtener items de una orden

---

## Fase 3: Servicios

Implementar:

- create_order
- add_item
- remove_item
- recalculate_total
- transition_order_state

---

## Fase 4: Lógica de Flujos

Implementar:

### Flujo MESA
- add_item → PREPARACION inmediato

### Flujo RAPIDO
- add_item → PENDIENTE
- transición a CONFIRMADO solo con pago total (validación futura)

---

## Fase 5: Integración con Mesas

- validar consistencia:
  - Order MESA ↔ DiningTable

---

## Fase 6: Invariantes

Validar:

- no modificar items PAGADO
- no CONFIRMADO sin pago total (validación placeholder)

---

## Fase 7: Testing

Tests obligatorios:

- creación de order
- creación de items
- cálculo de total
- flujos MESA vs RAPIDO
- restricciones de modificación
- transiciones de estado

---

## Fase 8: Validación

- tests passing
- uso de transaction.atomic
- sin lógica en models