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
- En cada vista de pago o de resumen de cuenta se debe visualizar la propina sugerida a modo informativo. Sin embargo, el pago ejecutado sera la fuente de verdad para determinar cuanta propina pago realmente el cliente.

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

Completada (con issue conocido en terminal de ventas)

## Modelo de datos

### PaymentMethod (nuevo)

| Campo | Tipo | Descripcion |
|---|---|---|
| tenant | FK(Tenant) | Pertenencia multitenant |
| nombre | CharField(50) | Nombre del medio de pago |
| activo | BooleanField | Habilitado/deshabilitado |
| orden | IntegerField | Orden de presentacion |

Restricciones: `unique_together = (tenant, nombre)`. Manager `TenantAwareManager`.

### Transaction (modificado)

Campos agregados:

| Campo | Tipo | Descripcion |
|---|---|---|
| payment_method | FK(PaymentMethod, PROTECT) | Medio de pago usado, nullable |
| tip_amount | DecimalField | Propina registrada en esta transaccion |

Validacion en `save()`: `payment_method.tenant_id` debe coincidir con `order.tenant_id`.

### Order (modificado)

Campo eliminado: `propina_monto`. Ya no se almacena propina a nivel de orden.

## Servicios

### payment_calculator.py

- **Eliminado** `set_tip(user, order, amount)`: la propina ya no se fija a nivel de orden.
- Mantenidos `calculate_iva_breakdown()` y `calculate_suggested_tip()`.

### payment.py

- `register_transaction()`: nuevos parametros `payment_method` (obligatorio) y `tip_amount` (opcional, default 0).
  - Valida que `payment_method` exista, este activo y pertenezca al tenant.
  - Valida que `tip_amount >= 0` (sin limite superior).
  - Registra ambos campos en la transaccion creada.
- `update_order_payment_state()`: renombradas variables internas de `total_paid`/`total_cuenta` a `total_consumo_paid`/`total_consumo`. El cierre se determina exclusivamente por consumo pagado vs total_bruto. La propina no afecta transiciones.

### order.py

- `create_order()`: eliminado parametro `propina_monto`.

## Selectors

### TransactionSelector (reescrito)

| Metodo | Retorno | Descripcion |
|---|---|---|
| `total_cuenta(order)` | `order.total_bruto` | Total de consumo sin propina |
| `total_consumo_paid(order)` | Suma de `monto` | Consumo pagado (excluye tip_amount) |
| `total_tip_paid(order)` | Suma de `tip_amount` | Propina total cobrada |
| `total_pending(order)` | `total_cuenta - total_consumo_paid` | Consumo pendiente |
| `suggested_tip(order)` | `total_bruto * 0.10` | Propina sugerida sobre total |
| `suggested_tip_pending(order)` | `total_pending * 0.10` | Propina sugerida sobre pendiente |
| `total_pending_with_tip(order)` | `total_pending + suggested_tip_pending` | Pendiente informativo con propina |
| `items_paid_amount(order)` | Suma de monto tipo PRODUCTOS | Monto pagado por productos |

## Vistas

### `_build_payment_context(order, tenant, table=None)` (nueva)

Funcion centralizada que construye el contexto comun para todas las vistas de pago. Incluye: desglose IVA, propinas pagadas/sugeridas, totales, items pagados/pendientes, transacciones y metodos de pago activos.

### `orden_procesar_pago()` (modificada)

- Lee `payment_method` y `tip_amount` del POST.
- Pasa ambos a `register_transaction()`.
- Separada logica de redireccion: `COMPLETADO` redirige (mesa -> salon, rapido -> terminal); `CONFIRMADO` en flujo rapido retorna modal actualizado sin redirigir (permite seguir operando).

### `_get_or_create_order_for_session()` (modificada)

- Query cambiada de `estado=ABIERTO` a `estado__in=Order.ACTIVE_STATES` para reutilizar ordenes en `PAGADO_PARCIAL` o `CONFIRMADO` en flujo rapido.

### Eliminada `orden_fijar_propina()`

Ya no existe endpoint para fijar propina a nivel de orden.

## Templates

### propina_input.html (nuevo)

Componente reusable de propina por pago:
- Input numerico de monto (siempre editable).
- 3 botones de modo: **Sin propina** (0%), **10%** (default), **Otro %** (input personalizado).
- Display "Total a pagar" con enfasis visual (borde, fondo claro, texto grande).
- JS recalcula total al cambiar modo, porcentaje, o escribir manualmente.

### modal_pago.html y terminal_modal_pago.html (reescritos)

- Eliminado detalle de "Pagos Realizados" (el modal es para ingresar pagos, no consultar).
- Boton de pago total: texto estatico "Registrar Pago".
- "Total a pagar" se actualiza dinamicamente arriba del boton.
- Pestaña "Por Productos": propina se recalcula automaticamente al seleccionar/deseleccionar items (usa MutationObserver en `#selected-total`).

### cuenta_actualizada.html y mesa_pedido.html (reordenados)

Nuevo orden de secciones:
1. **Productos**: pagados y pendientes.
2. **Desglose**: Neto, IVA, Total Consumo, Propina sugerida 10%.
3. **Pagos**: tabla con columnas Tipo | Forma de pago | Consumo | Propina | Total. Footer con totales.
4. **Pendiente de Pago**: Consumo pendiente, Propina sugerida 10%, Total pendiente.

## Tests

| Archivo | Tests | Descripcion |
|---|---|---|
| `test_payment_calculator.py` | 14 | IVA, propina sugerida, closure por consumo, tip por transaccion |
| `test_payment_methods.py` | 14 | Seed, modelo, tenant isolation, transacciones con payment_method y tip |
| `test_payments.py` | 14 | Flujo completo de pagos actualizado a nueva API |
| `test_hito11_corrections.py` | 7 | Corregidos para incluir payment_method |
| `test_comanda.py` | 8 | Corregidos para incluir payment_method |

Total: 49 tests pasando.

## Migraciones

| Migracion | Descripcion |
|---|---|
| `0005_paymentmethod.py` | Creacion de modelo PaymentMethod |
| `0006_transaction_tip_and_method.py` | Campos tip_amount y payment_method en Transaction |
| `0007_remove_order_propina_monto.py` | Eliminacion de campo propina_monto de Order |

## Issue conocido: Terminal de ventas no libera el carrito tras pago completo

**Descripcion:** Cuando se registra un pago TOTAL o ABONO que completa el consumo en flujo rapido, la orden pasa a estado `CONFIRMADO` o `COMPLETADO`, pero la terminal de ventas no resetea el carrito ni permite iniciar una nueva orden. La funcion `_get_or_create_order_for_session` reutiliza la orden existente en `ACTIVE_STATES`, lo que impide avanzar al siguiente cliente.

**Causa raiz:** La logica actual de terminal de ventas asume un unico pedido por sesion (`session['order_id']`). Al completar un pago, la orden queda en estado terminal pero la sesion sigue apuntando a ella.

**Impacto:** No se puede procesar un nuevo pedido sin recargar la pagina o limpiar la sesion manualmente.

**Solucion requerida:** Implementar gestion multi-orden en terminal de ventas:
1. Al completar una orden, marcarla como cerrada y limpiar `session['order_id']`;
2. Permitir crear una nueva orden automaticamente al agregar el primer producto;
3. Opcionalmente, mantener un historial de ordenes del turno para consulta.

**Estado:** Pendiente de implementacion en tarea futura dedicada a la terminal de ventas.
