# Current Milestone

## Milestone

Hito 11 — Módulo de Pagos y Cierre de Cuenta

## Estado general

- Hitos 01-11 completados
- Hito 11: COMPLETADO
  - Fase 1: Backend Core ✅
  - Fase 2: Views/URLs ✅
  - Fase 3: Frontend Templates ✅
  - Fase 4: Testing ✅
  - Fase 5: Validación ✅

---

## Phase

Completed

---

## Status

completed

---

## Fecha inicio

2026-04-16

---

## Fecha completion

2026-04-17

---

## Decisión de diseño

- Propina incluida en total_cuenta: total_cuenta = total_bruto + propina_monto
- Condición de completado: total_paid >= total_cuenta
- TransactionSelector.total_pending() usa total_cuenta
- fetch() sobre hx-post para todos los formularios de pago (confiabilidad CSRF)
- Selección de template por order.table_id (mesa vs terminal)
- Propina 10% auto-aplicada al abrir modal si propina_monto == 0
- Sticky bar en lugar de fixed para evitar solapamiento con sidebar
- 100 tests pasando (15 payment_calculator + 7 hito11_corrections + 78 existentes)