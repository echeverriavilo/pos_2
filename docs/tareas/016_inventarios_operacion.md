# 016 - Operacion de inventarios

## Objetivo

Implementar vistas y flujos para consultar inventarios, capturar tomas de inventario y modificar stocks.

## Contexto

Esta tarea extiende la base de inventario ya implementada, agregando operacion diaria y herramientas de ajuste desde UI.

## Dependencias

- `002_catalogo_inventario_base.md`
- `014_vistas_crud_backoffice.md`

## Reglas aplicables

- todo cambio de stock debe seguir siendo trazable;
- las modificaciones de inventario deben respetar tenant y permisos;
- la UI no puede mutar stock fuera de los services de inventario.

## Plan de implementacion

- implementar vistas de consulta de stock;
- implementar flujos de toma/captura de inventario;
- implementar ajustes manuales controlados;

## Criterios de aceptacion

- se puede consultar inventario actual;
- se puede registrar una toma de inventario;
- se puede modificar stock mediante operaciones controladas;
- las operaciones quedan trazables;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: conteos parciales o ciclicos;
- pendiente de definicion: politica de auditoria y aprobaciones;
- pendiente de definicion: frecuencia operativa esperada.
