# 015 - Pantallas de cocina y barra

## Objetivo

Implementar pantallas operativas de cocina y barra que reemplacen o complementen a las impresoras de comanda.

## Contexto

Esta tarea extiende y reorienta la tarea 10. Reutiliza el backend de comandas ya implementado y agrega el modelo operativo de estaciones con pantalla.

## Dependencias

- `010_comandas_y_dispositivos_salida.md`
- `014_vistas_crud_backoffice.md`

## Reglas aplicables

- cada tenant puede tener cero, una o varias cocinas y/o barras;
- cada producto debe poder mapearse a una cocina o barra;
- cada pantalla debe mostrar pedidos pendientes y permitir cambios de estado;
- la estacion puede ocultar items al llegar a `LISTO` o `ENTREGADO` segun configuracion del tenant.

## Plan de implementacion

- extender el modelo de comandas hacia estaciones operativas con pantalla;
- implementar vistas de cocina y barra para operar estados;
- permitir configuracion tenant-aware de estaciones y visibilidad;

## Criterios de aceptacion

- el tenant puede configurar estaciones de cocina/barra;
- los productos se enrutan a la estacion correspondiente;
- la pantalla muestra pedidos pendientes;
- la estacion puede cambiar estados segun la configuracion definida;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: modelo exacto de estacion;
- pendiente de definicion: reglas finales de desaparicion y estados opcionales por tenant;
- esta tarea complementa/reemplaza la UI pendiente de la tarea 10, no su backend ya implementado.
