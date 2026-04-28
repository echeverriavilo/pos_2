# 017 - Informes y reporteria

## Objetivo

Permitir la visualizacion y personalizacion de informes operativos y financieros del tenant.

## Contexto

La tarea cubre reportes de ventas, cierres de caja, ventas por producto, inventarios y otras vistas agregadas del negocio.

## Dependencias

- `013_apertura_y_cierre_caja.md`
- `016_inventarios_operacion.md`

## Reglas aplicables

- los informes deben respetar tenant y permisos;
- la informacion debe poder filtrarse o agruparse;
- los datos deben provenir del dominio operativo real.

## Plan de implementacion

- definir informes base del MVP;
- implementar vistas de consulta y filtros;
- integrar agrupaciones y resumenes principales;

## Criterios de aceptacion

- existen informes de ventas, cierres de caja, ventas por producto e inventarios;
- el usuario puede filtrar o agrupar informacion segun el informe;
- los resultados son consistentes con los datos operativos;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: filtros exactos por informe;
- pendiente de definicion: exportaciones;
- pendiente de definicion: snapshots o cierres historicos de reportes.
