# Status — Hito 02

Estado: in progress

## Avance sesión
- App `catalog` añadida con modelos tenant-aware `Category`, `Product`, `Ingredient` y `StockMovement`.
- Services CRUD + `InventoryService` (ingreso/ajuste/venta) actualizan `Product.stock_actual` en transacciones, bloqueando stock negativo de inventariables y conservando historial.
- Selectores tenant-aware y tests (pytest) cubren aislamiento de tenants, movimientos y validaciones de stock.
- `TenantAwareManager` adaptado para exponer `.for_tenant()` y `specs/domain/data-model.md` ahora refleja los tipos de movimiento acordados.
  - La app se registró en `INSTALLED_APPS` y se generaron migraciones.

## Pruebas
- `.venv/bin/python -m pytest`

## Decisiones clave
1. Se mantiene `precio_bruto` en `Product` y no se calcula neto hasta respuestas posteriores.
2. `StockMovement.tipo` cubre solo `INGRESO`, `AJUSTE`, `VENTA` porque el hito solo pide esos tres movimientos.
3. `InventoryService` expone métodos separados por tipo de movimiento (ingreso/ajuste/venta), no se expone lógica de inventario en los modelos ni se usan endpoints aún.
4. `Product.stock_actual` guarda el estado actual del stock para consultas rápidas y solo cambia vía movimientos documentados.
