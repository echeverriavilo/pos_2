# Tasks — Hito 3: DiningTable

- [x] Crear app `orders`, modelo `Order` y servicio canónico `orders.services.create_order_for_table` con contratos claros y estados activos definidos.
- [x] Crear modelo `DiningTable` (tenant-aware) con enum de estados (`DISPONIBLE`, `OCUPADA`, `PAGANDO`, `RESERVADA`) y selectores reutilizando el patrón tenant-aware del inventario.
- [x] Implementar selector `get_active_order_for_table(table)` que filtra por mesa, tenant y estados activos.
- [x] Implementar servicios `create_table`, `open_table`, `set_table_paying` y `reopen_table`, validando invariantes y reutilizando el servicio de órdenes.
- [x] Verificar invariantes en cada servicio (mesa DISPONIBLE sin order activo, OCUPADA/PAGANDO con order activo, único order activo) y documentar en status/decisions.
- [x] Escribir tests que cubran la apertura de mesa, transiciones y violaciones de invariantes.
