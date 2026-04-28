# 008 - Terminal de ventas de flujo rapido

## Objetivo

Construir la interfaz de toma de pedidos de alta velocidad para el flujo rapido.

## Contexto

La tarea conecta catalogo, ordenes y UI HTMX para operar sin recarga completa.

## Dependencias

- `002_catalogo_inventario_base.md`
- `004_motor_ordenes_y_items.md`
- `007_shell_pwa_y_autenticacion.md`

## Reglas aplicables

- no inventar estado de negocio en frontend;
- carrito reactivo apoyado por backend;
- calculo de totales consistente con la orden real.

## Plan de implementacion

- crear vista de terminal con grid de productos;
- agregar filtro por categorias y buscador;
- implementar carrito HTMX para agregar/quitar items;
- cubrir integracion del flujo completo.

## Criterios de aceptacion

- grid de productos y categorias funcional;
- buscador por nombre;
- agregar/quitar productos sin recarga;
- calculo correcto de totales;
- navegacion fluida entre categorias.

## Validacion requerida

- `pytest` de terminal de ventas

## Estado

Completado

## Notas y resultados

- la tarea quedo operativa con tests de terminal pasando;
- el backend expone endpoints y selectores para soportar la UI.
