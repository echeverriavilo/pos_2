# Execution Plan — Hito 3: DiningTable

## Fase 1: Modelo

- Implementar modelo DiningTable
- Definir enum de estados
- Agregar tenant FK

---

## Fase 2: Selectors

- Obtener mesas por tenant
- Obtener mesa con order activo

---

## Fase 3: Servicios

Implementar en services/:

- create_table
- open_table
- set_table_paying
- reopen_table

Validaciones:

- estado actual
- existencia de order activo
- tenant consistency

---

## Fase 4: Integración con Order (mínima)

- open_table debe crear Order
- NO implementar lógica completa de Order (fuera de scope)

---

## Fase 5: Invariantes

Validar en servicios:

- mesa DISPONIBLE → no order activo
- mesa OCUPADA/PAGANDO → existe order activo

---

## Fase 6: Testing

Tests obligatorios:

- creación de mesa
- apertura de mesa
- transición OCUPADA → PAGANDO
- consistencia con Order
- violaciones de invariantes

---

## Fase 7: Validación

- todos los tests pasan
- no hay lógica en models
- uso de transaction.atomic en operaciones críticas