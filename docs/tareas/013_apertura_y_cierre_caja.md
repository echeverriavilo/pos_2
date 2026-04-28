# 013 - Apertura y cierre de caja

## Objetivo

Implementar la operacion de cajas por tenant, incluyendo aperturas de turno, asociacion obligatoria de movimientos y cierre con cuadratura.

## Contexto

Cada tenant puede operar con una o varias cajas. Cada caja puede soportar uno o ambos flujos del sistema y debe tener un control explicito de apertura y cierre.

## Dependencias

- `005_pagos_transacciones.md`
- `012_mejoras_pago_y_formas_pago.md`

## Reglas aplicables

- cada tenant puede tener multiples cajas;
- cada caja puede soportar uno o ambos flujos;
- no se permiten movimientos sin una apertura activa;
- cada apertura debe cerrarse con una cuadratura de caja.

## Plan de implementacion

- definir dominio de caja, apertura y cierre;
- asociar pagos y movimientos a una apertura activa;
- implementar apertura de turno y cierre con resumen de movimientos;

## Criterios de aceptacion

- el tenant puede crear y operar multiples cajas;
- no se puede registrar un movimiento sin apertura activa;
- el cierre de caja muestra la cuadratura del turno;
- los movimientos quedan asociados a la apertura correspondiente;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: multiples turnos simultaneos por caja;
- pendiente de definicion: diferencias toleradas y flujo de reapertura;
- pendiente de definicion: alcance exacto de "movimiento" para caja versus inventario.
