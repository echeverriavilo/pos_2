# Status — Hito 3: DiningTable

## Estado general
Completed (modelos y servicios listos, pruebas verdes y decisiones registradas).

---

## Progreso

- Modelo: COMPLETADO (DiningTable tenant-aware, enum de estados, constraints) y Order mínimo con estados/flujo.
- Selectores: COMPLETADO (listado filtrado por tenant y `get_active_order_for_table`).
- Servicios: COMPLETADO (create_table, open_table, set_table_paying, reopen_table) con transacciones e invariantes revisadas.
- Integración Order: COMPLETADO (`open_table` delega en `orders.services.create_order_for_table`).
- Testing: COMPLETADO (`python -m pytest apps/dining/tests/test_tables.py`).
- Documentación: COMPLETADO (tasks/status/decisions actualizados).

---

## Dependencias

- Nueva app `orders` con modelo y servicio minimalistas para sostener el flujo de mesa.

---

## Riesgos

- La definición de "order activo" (ABIERTO/PAGADO_PARCIAL/CONFIRMADO) debe seguir alineada con los futuros cierres de flujo (OrderBatch/Comanda en hito 4).

---

## Bloqueos

- Ninguno
