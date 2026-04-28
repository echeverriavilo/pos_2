# 011 - Pago parcial y cierre de cuenta

## Objetivo

Implementar la interfaz visual de pagos, propinas y cierre de cuenta para ordenes con mesa y de flujo rapido.

## Contexto

La tarea completa la experiencia operativa del modulo de pagos sobre el backend ya existente.

## Dependencias

- `005_pagos_transacciones.md`
- `007_shell_pwa_y_autenticacion.md`
- `008_terminal_ventas_flujo_rapido.md`
- `009_mapa_salon_y_pedido_mesa.md`

## Reglas aplicables

- el desglose debe mostrar subtotal, IVA, propina y total;
- `total_cuenta = total_bruto + propina_monto`;
- la propina es opcional, con sugerencia de 10%;
- los templates deben diferenciar flujo mesa y rapido cuando cambie el cierre.

## Plan de implementacion

- crear modal de pago y selector de items;
- agregar formulario de abono;
- integrar calculo de IVA y propina;
- actualizar ticket/pre-cuenta tras cada pago;
- cubrir ambos flujos con tests de integracion.

## Criterios de aceptacion

- modal de pago con desglose completo;
- pago por productos y por abono funcional;
- propina sugerida, editable y opcional;
- ticket actualizado tras cada pago;
- estados de la orden cambian correctamente;
- pruebas de integracion de pagos.

## Validacion requerida

- `pytest` del modulo de pagos y sus integraciones

## Estado

Completado

## Notas y resultados

- el sistema calcula el saldo sobre `total_cuenta`;
- la UI de pagos se ajusta segun si la orden tiene mesa o es de flujo rapido;
- las mejoras de propina por pago y formas de pago continúan en `012_mejoras_pago_y_formas_pago.md`.
