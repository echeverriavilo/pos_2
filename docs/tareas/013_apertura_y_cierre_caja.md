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

Completado — correcciones de cuadratura, propina y UI implementadas (2026-04-28).

## Notas y resultados

### Decisiones adoptadas (2026-04-28)

1. **Ubicacion de modelos**: CashRegister, CashSession, CashMovement y CashCloseDetail en `apps/orders/` (junto a Transaction y PaymentMethod) dado que CashMovement tiene FK a Transaction y el pago exige CashSession abierta.
2. **Sesiones simultaneas**: Solo 1 sesion abierta por caja. No se permite abrir una segunda sesion si ya existe una abierta en la misma caja.
3. **Cierre con descuadre**: Se permite cerrar una sesion aunque la cuadratura no calce. Se registra `monto_cierre_declarado` y se calcula `diferencia = monto_cierre_declarado - monto_cierre_calculado`. La diferencia queda trazada pero no bloquea el cierre.
4. **Reapertura**: No se permite reabrir una sesion cerrada. Si hubo error, se debe crear una nueva sesion.
5. **Alcance de movimientos**: Solo monetarios. Tipos: INGRESO, EGRESO, AJUSTE. vinculados opcionalmente a una Transaction.
6. **Propina incluida en movimiento de caja**: El monto de un CashMovement tipo INGRESO automatico de pago incluye `transaction_amount + tip_amount`, no solo el consumo.
7. **Cuadratura por medio de pago**: El cierre de caja cuadra por cada PaymentMethod. Se ingresa el monto declarado por medio, se compara con el total sistema (incluyendo movimientos manuales y automaticos, con EGRESOs restando) y se registra la diferencia con comentario obligatorio por medio.
8. **Movimientos manuales — semantica**: INGRESO y EGRESO son movimientos en efectivo (auto-asignados al PaymentMethod "Efectivo"). AJUSTE requiere seleccion explicita de medio de pago. El comentario es obligatorio para todos los movimientos manuales.
9. **Signo de AJUSTE**: El monto siempre es positivo; el signo se controla via radio "Credito (+)" / "Debito (-)" en la UI, y la vista niega el monto antes de pasarlo al servicio si es debito.
10. **Flujo de cierre en 2 pasos**: (1) Pantalla de ingreso de datos con boton "Revisar Cierre" → (2) Pantalla de revision readonly con botones "Modificar" y "Confirmar Cierre de Caja". El cierre solo se ejecuta al confirmar.
11. **Formato de moneda**: En toda la app, el formato de moneda es `$X.XXX` (signo peso, separador de miles con punto, sin decimales). Implementado via template tag `currency` en `apps/core/templatetags/currency.py`.
12. **Columnas ocultas**: En la pantalla de cierre, las columnas "Total sistema" y "Diferencia" estan ocultas por defecto con un boton toggle unificado ("Columnas").
13. **Monto declarado por defecto**: 0. El cajero debe contar y declarar activamente cada medio de pago.
14. **Historial de cierres**: Vista independiente (`sesiones_cerradas`) que lista todas las sesiones CERRADA con sus montos, diferencias y acceso al detalle individual.

### Implementado (sesiones 2026-04-28)

#### Modelos (4 entidades)

- **CashRegister**: `apps/orders/models/cash_register.py`. Campos: tenant, nombre, soporta_flujo_mesa, soporta_flujo_rapido, activo.
- **CashSession**: `apps/orders/models/cash_session.py`. Campos: tenant, cash_register, opened_by, closed_by, opened_at, closed_at, estado (ABIERTA/CERRADA), monto_apertura, monto_cierre_declarado, diferencia, comentario_cierre.
- **CashMovement**: `apps/orders/models/cash_movement.py`. Campos: tenant, cash_session, transaction (nullable), payment_method (nullable), tipo (INGRESO/EGRESO/AJUSTE), monto, descripcion.
- **CashCloseDetail**: `apps/orders/models/cash_close_detail.py`. Campos: tenant, cash_session, payment_method, monto_sistema, monto_declarado, diferencia, comentario. Unique (cash_session, payment_method).

#### Migraciones

- 0008: modelos CashRegister, CashSession, CashMovement.
- 0009: seed de permisos (manage_cash_registers, open_cash_session, close_cash_session) en roles administrador y cajero existentes.
- 0010: CashCloseDetail + campo comentario_cierre en CashSession.
- 0011: campo payment_method (FK PaymentMethod) en CashMovement.
- 0012: campo comentario en CashCloseDetail.

#### Permisos

- `manage_cash_registers`, `open_cash_session`, `close_cash_session` en `SystemActions`.
- Asignados a roles administrador y cajero via migracion 0009.

#### Servicios

- **cash_register.py**: `create_cash_register`, `update_cash_register`, `toggle_cash_register`. Validan tenant, permisos y reglas (al menos un flujo, nombre obligatorio, no desactivar con sesion abierta).
- **cash_session.py**: `open_cash_session` (valida caja activa y sin sesion abierta), `close_cash_session` (recibe payment_details con comentario por medio, calcula breakdown con apertura en Efectivo, crea CashCloseDetail, exige comentario si hay diferencia), `register_cash_movement` (valida monto > 0, descripcion obligatoria para manuales, payment_method obligatorio para AJUSTE, auto-asigna Efectivo para INGRESO/EGRESO, signo procesado en vista), `get_session_summary`.
- **payment.py**: `register_transaction` valida CashSession abierta, crea CashMovement tipo INGRESO con `monto = transaction_amount + tip_amount` y `payment_method = transaction.payment_method`.
- **order.py**: `transition_order_state` invoca `update_order_payment_state`.

#### Selectores

- **cash_register.py**: `CashRegisterSelector.list_cash_registers`.
- **cash_session.py**: `CashSessionSelector.get_active_session_for_register`, `get_active_session_for_tenant`, `get_active_session_for_order` (filtra por caja compatible con el flujo de la orden), `get_session_payment_breakdown` (agrupa por payment_method, INGRESOs y AJUSTEs suman, EGRESOs restan vía Case/When), `list_session_movements`.

#### Vistas (8) y URLs

| URL | Vista | Funcion |
|---|---|---|
| `caja/` | `caja_lista` | Lista cajas y sesiones activas |
| `caja/crear/` | `caja_crear` | Crear caja (POST) |
| `caja/<pk>/editar/` | `caja_editar` | Editar caja |
| `caja/<pk>/toggle/` | `caja_toggle_activa` | Activar/desactivar (POST) |
| `caja/sesion/abrir/` | `sesion_abrir` | Abrir sesion |
| `caja/sesion/<id>/` | `sesion_detalle` | Detalle con movimientos, filtro por tipo, close_details si CERRADA |
| `caja/sesion/<id>/cerrar/` | `sesion_cerrar` | GET: formulario ingreso; POST: renderiza confirmacion |
| `caja/sesion/<id>/confirmar/` | `sesion_confirmar` | POST: ejecuta close_cash_session |
| `caja/sesion/<id>/movimiento/` | `sesion_movimiento` | GET: form parcial; POST: registra movimiento |
| `caja/cierres/` | `sesiones_cerradas` | Historial de sesiones cerradas |

#### Templates (9)

- `cash_registers.html`: lista de cajas + modal nueva caja + enlace a historial de cierres.
- `cash_register_form.html`: formulario edicion de caja.
- `cash_session_open.html`: formulario apertura de sesion.
- `cash_session_close.html`: formulario ingreso de datos (paso 1). Tabla por medio de pago con inputs monto declarado (default 0) y explicacion, resumen con formula de cuadratura (JS en vivo), columnas "Total sistema" y "Diferencia" ocultas con toggle, boton "Revisar Cierre".
- `cash_session_close_confirm.html`: revision readonly (paso 2). Tabla con datos ingresados, resumen calculado en backend, hidden fields, alerta irreversible, botones "Modificar" y "Confirmar Cierre de Caja".
- `cash_session_detail.html`: detalle con info de sesion, resumen de cuadratura (si CERRADA), tabla CashCloseDetail, movimientos con filtro por tipo y columna "Medio", modal movimiento manual con radios signo para AJUSTE.
- `sesiones_cerradas.html`: historial de cierres con tabla (caja, abierto/cerrado por, fechas, montos, diferencia, ver).
- `partials/cash_movement_form.html`: formulario parcial con tipo, medio de pago (visible solo AJUSTE), radios signo (visible solo AJUSTE), monto, descripcion.

#### Template tags

- `apps/core/templatetags/currency.py`: filter `currency` (`$X.XXX`, separador de miles con punto, sin decimales) y filter `get_item` (diccionario por clave).

#### Sidebar

- Enlace "Cajas" en `grastro/templates/grastro/base.html`.

#### Tests

- 31 tests en `apps/orders/tests/test_cash_session.py`.
- Suite completa: 144 tests pasando.
- Cobertura: CRUD cajas, sesiones (abrir, cerrar, cuadratura exacta/con diferencia, no reabrir), movimientos manuales (validaciones, payment_method, signo), integracion pago-sesion, propina en CashMovement, CashCloseDetail, comentario obligatorio/opcional, breakdown.
