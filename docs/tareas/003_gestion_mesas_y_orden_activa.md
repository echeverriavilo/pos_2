# 003 - Gestion de mesas y orden activa

## Objetivo

Implementar `DiningTable`, sus transiciones y la relacion canonica con una orden activa por mesa.

## Contexto

La tarea formaliza el flujo con mesas y prepara la integracion con el motor de ordenes.

## Dependencias

- `001_base_multitenancy_identidad.md`
- `002_catalogo_inventario_base.md`

## Reglas aplicables

- una mesa disponible no puede tener orden activa;
- una mesa ocupada o pagando debe tener exactamente una orden activa;
- abrir mesa crea orden `ABIERTO` en flujo `MESA`.

## Plan de implementacion

- crear `DiningTable` tenant-aware;
- introducir orden minima y selector de orden activa;
- implementar `create_table`, `open_table`, `set_table_paying` y `reopen_table`;
- validar invariantes de mesa y tenant en servicios y tests.

## Criterios de aceptacion

- se puede crear mesa `DISPONIBLE`;
- abrir mesa cambia a `OCUPADA` y crea orden asociada;
- `OCUPADA -> PAGANDO -> OCUPADA` funciona segun flujo;
- no puede existir mas de una orden activa por mesa;
- existe cobertura de invariantes.

## Validacion requerida

- `pytest apps/dining/tests/test_tables.py`

## Estado

Completado

## Notas y resultados

- la definicion de orden activa quedo fijada en `ABIERTO`, `PAGADO_PARCIAL` y `CONFIRMADO`;
- `open_table` delega la creacion de orden a `orders.services.create_order_for_table`.
