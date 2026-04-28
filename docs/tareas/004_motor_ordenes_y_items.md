# 004 - Motor de ordenes y items

## Objetivo

Implementar el dominio completo de `Order` y `OrderItem`, con estados validos, servicios y consistencia por flujo.

## Contexto

Extiende la orden minima introducida para mesas hacia un motor reutilizable para flujo con mesa y flujo rapido.

## Dependencias

- `003_gestion_mesas_y_orden_activa.md`

## Reglas aplicables

- servicios canonicos para crear orden, agregar/quitar items, recalcular total y transicionar estado;
- `OrderItem` inmutable cuando esta pagado;
- no se permiten transiciones fuera de las definidas por flujo.

## Plan de implementacion

- completar modelos `Order` y `OrderItem`;
- crear selectores por tenant, mesa e items;
- implementar servicios explicitos de ordenes;
- recalcular total bruto y validar cambios de estado;
- cubrir flujos de mesa y rapido.

## Criterios de aceptacion

- se puede crear orden con o sin mesa;
- agregar y quitar items modifica el total correctamente;
- las transiciones de estado respetan las reglas del flujo;
- existen tests de servicios y transiciones.

## Validacion requerida

- `pytest apps/orders`

## Estado

Completado

## Notas y resultados

- la logica principal de ordenes vive en services;
- el dominio quedo listo para pagos, stock y comandas.
