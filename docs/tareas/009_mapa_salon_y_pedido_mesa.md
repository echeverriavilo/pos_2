# 009 - Mapa de salon y pedido de mesa

## Objetivo

Implementar la interfaz visual para operar el flujo con mesas y abrir pedidos desde el mapa del salon.

## Contexto

La tarea reutiliza `DiningTableService` y el dominio de ordenes para la operacion del garzon.

## Dependencias

- `003_gestion_mesas_y_orden_activa.md`
- `004_motor_ordenes_y_items.md`
- `007_shell_pwa_y_autenticacion.md`

## Reglas aplicables

- colores y estados de mesa deben reflejar el dominio real;
- abrir mesa y agregar productos debe respetar las invariantes del flujo con mesa;
- si una mesa esta `PAGANDO` y recibe productos, vuelve a `OCUPADA`.

## Plan de implementacion

- crear vista de mapa de salon con grid visual;
- agregar modal o side panel de apertura/pedido;
- integrar con servicios de mesa y orden;
- redirigir al pedido especifico de la mesa;
- cubrir flujo UI de apertura y actualizacion.

## Criterios de aceptacion

- grilla de mesas renderizada;
- apertura de mesa funcional;
- redireccion a pedido de mesa especifica;
- cambios de estado visibles;
- pruebas de integracion de UI.

## Validacion requerida

- `pytest` de dining/orders UI

## Estado

Completado

## Notas y resultados

- se adopto un side panel mobile-first para nuevo pedido;
- se corrigio el layout para evitar dependencias sobre `.d-flex` generica.
