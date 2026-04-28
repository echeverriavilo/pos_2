# 012 - Mejoras de pago y formas de pago

## Objetivo

Mejorar la experiencia operativa de pagos, moviendo la logica de propina a nivel de pago e incorporando formas de pago configurables por tenant.

## Contexto

Esta tarea extiende la tarea 11. No reemplaza el modulo de pagos existente, sino que corrige su modelo operativo y agrega configuracion tenant-aware para medios de pago.

## Dependencias

- `005_pagos_transacciones.md`
- `011_pago_parcial_y_cierre_cuenta.md`

## Reglas aplicables

- la propina debe operar por pago, no por mesa;
- toda transaccion debe indicar una forma de pago;
- deben existir formas de pago por defecto: efectivo, tarjeta debito, tarjeta credito y transferencia;
- cada tenant debe poder gestionar su propio catalogo de formas de pago.

## Plan de implementacion

- ajustar el flujo de pagos para desacoplar propina del nivel global de orden;
- introducir CRUD de formas de pago por tenant;
- integrar la seleccion de forma de pago en los pagos existentes;

## Criterios de aceptacion

- la propina puede aplicarse y registrarse por pago;
- cada pago registra su forma de pago;
- el tenant puede crear, editar, activar o desactivar sus formas de pago;
- el sistema inicializa las formas de pago por defecto para nuevos tenants;

## Validacion requerida

- `pytest` del modulo de pagos y sus integraciones

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: modelo exacto de persistencia de propina por pago;
- pendiente de definicion: reglas de reversa, anulacion o reporting de formas de pago.
