# 010 - Comandas y dispositivos de salida

## Objetivo

Implementar el backend de dispositivos, configuraciones de salida y generacion automatica de comandas.

## Contexto

La tarea cubre cocina/barra desde el dominio, aunque la UI completa de comandas sigue parcial.

## Dependencias

- `004_motor_ordenes_y_items.md`
- `005_pagos_transacciones.md`

## Reglas aplicables

- flujo mesa genera comandas al agregar items;
- flujo rapido genera comandas al confirmar pago total;
- se debe respetar prioridad y dispositivo por defecto;
- no generar duplicados item-dispositivo.

## Plan de implementacion

- crear modelos de dispositivo, configuracion y comanda;
- implementar servicios CRUD y de generacion automatica;
- agregar selectores del modulo;
- integrar generacion con add item y confirmacion de orden;
- cubrir reglas de asignacion y duplicidad.

## Criterios de aceptacion

- se pueden configurar dispositivos de salida;
- productos/categorias se asignan correctamente a dispositivos;
- existe dispositivo por defecto por tenant;
- las comandas se generan en ambos flujos segun reglas;
- hay tests del modulo.

## Validacion requerida

- `pytest` del modulo de comandas

## Estado

Completado parcial

## Notas y resultados

- el backend de comandas esta implementado y probado;
- la UI especializada de cocina/barra sigue pendiente y se continua en `015_pantallas_cocina_y_barra.md`.
