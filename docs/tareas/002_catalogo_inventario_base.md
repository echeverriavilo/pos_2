# 002 - Catalogo e inventario base

## Objetivo

Implementar catalogo de productos e inventario tenant-aware con control de stock y trazabilidad de movimientos.

## Contexto

La tarea introduce `catalog` y el servicio de inventario sobre el dominio base multitenant.

## Dependencias

- `001_base_multitenancy_identidad.md`

## Reglas aplicables

- `stock_actual` solo cambia mediante `StockMovement`;
- no permitir stock negativo en productos inventariables;
- toda mutacion de stock debe ser atomica.

## Plan de implementacion

- crear `Category`, `Product`, `Ingredient` y `StockMovement`;
- implementar CRUD base;
- implementar `InventoryService` para ingreso, ajuste y venta;
- adaptar managers para filtros por tenant;
- cubrir validaciones de stock y aislamiento.

## Criterios de aceptacion

- se pueden crear categorias y productos;
- un producto puede ser inventariable o no;
- se registran movimientos de ingreso y ajuste;
- `stock_actual` se actualiza correctamente;
- existen tests de inventario y multitenancy.

## Validacion requerida

- `pytest`

## Estado

Completado

## Notas y resultados

- `precio_bruto` se mantiene como valor canonico del producto;
- los movimientos activos del hito son `INGRESO`, `AJUSTE` y `VENTA`.
