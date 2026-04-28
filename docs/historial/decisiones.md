# Decisiones Persistentes

## 2026-04-10 - Base multitenant y acceso de plataforma

- Se crea `apps.core` con `Tenant`, `Role`, `Membership`, `StaffTenantAccess` y `CustomUser`.
- El tenant se resuelve por subdominio con middleware y contexto de tenant.
- `platform_staff` puede bypassar tenant solo mediante logica explicita.

## 2026-04-12 - Inventario con stock persistido

- `Product.stock_actual` se mantiene persistido.
- Todo cambio de stock debe registrarse mediante `StockMovement`.
- `InventoryService` expone operaciones separadas por tipo de movimiento y bloquea stock negativo cuando corresponde.

## 2026-04-13 - Definicion de orden activa y separacion mesa/orden

- Una orden activa para mesa es una orden en `ABIERTO`, `PAGADO_PARCIAL` o `CONFIRMADO`.
- La creacion de orden de mesa se centraliza en `orders.services.create_order_for_table`.
- Las invariantes mesa-orden se mantienen en el servicio de mesas.

## 2026-04-13 - Motor de ordenes orientado a services

- `OrderItem` fuerza tenant desde `Order`.
- La logica principal de ordenes vive en services explicitos para crear, agregar items, quitar items, recalcular y transicionar estado.

## 2026-04-15 - Autorizacion en services

- Se introducen `Permission` y `RolePermission`.
- Todos los servicios de dominio relevantes validan tenant y permiso a traves de `user`.
- `platform_staff` bypassa tenant, no permisos.

## 2026-04-15 - Frontend base server-rendered

- Bootstrap e iconos se instalan localmente.
- El sistema usa layout base responsive, login propio y dashboard server-rendered.
- No se adopta CDN ni SPA.

## 2026-04-16 - Comandas por dispositivo

- Se introduce backend de dispositivos, configuraciones y comandas.
- La generacion de comandas ocurre al agregar items en flujo mesa y al confirmar en flujo rapido.
- La resolucion de dispositivo respeta prioridad y default por tenant.

## 2026-04-16 - Total de cuenta como base de pago

- El total de pago del sistema es `total_bruto`. La propina es voluntaria y no forma parte del total obligatorio.
- `total_pending` se calcula como `total_bruto - total_consumo_paid` (sin incluir propina).
- El cierre de mesa se determina cuando `total_consumo_paid >= total_bruto`.

## 2026-04-17 - Propina sugerida por defecto

- La propina sugerida es el 10% del total_bruto.
- La propina se registra por transaccion (`Transaction.tip_amount`), no por orden.
- La UI de propina por pago ofrece: Sin propina (0%), 10% (default), Otro %, input manual siempre editable.
- El "Total a pagar" en cada pago es consumo de esa transaccion + propina de esa transaccion.

## 2026-04-17 - Flujos de cierre por tipo de orden

- En flujo mesa, el pago total habilita cierre hacia `COMPLETADO`.
- En flujo rapido, el pago total lleva a `CONFIRMADO` antes de la entrega final.

## 2026-04-28 - Reordenamiento del roadmap MVP

- La tarea de PWA/Bluetooth/Offline sale del tramo activo del MVP y pasa a backlog posterior como `xx_pwa_bluetooth_offline.md`.
- El roadmap activo continua con tareas 12 a 21 enfocadas en pagos, cajas, backoffice, cocina/barra, inventarios, reporteria, configuracion tenant y panel de plataforma.
- El `spec_maestro` se alinea con propina por pago, formas de pago tenant-aware, caja operativa y estaciones de cocina/barra.

## 2026-04-28 - Propina opera por transaccion, no por orden

- Eliminada la logica de propina por orden (`order.propina_monto`, `set_tip()`).
- La propina se registra por transaccion (`Transaction.tip_amount`).
- El cierre de mesa se determina exclusivamente por `total_consumo_paid >= total_bruto`; la propina es voluntaria y no afecta transiciones de estado.
- La propina sugerida (10%) es informativa y aparece en desglose de cuenta y modal de pagos.
- **Issue conocido:** Terminal de ventas no libera el carrito tras pago completo. Requiere gestion multi-orden en tarea futura.

## 2026-04-28 - Formas de pago obligatorias por transaccion

- Toda transaccion debe registrar un `PaymentMethod`. No se permiten pagos sin forma de pago.
- `PaymentMethod` es tenant-aware: cada tenant gestiona su propio catalogo.
- Formas de pago por defecto: Efectivo, Tarjeta Debito, Tarjeta Credito, Transferencia.
- El campo `payment_method` en `Transaction` es `PROTECT` (no se puede eliminar un metodo con transacciones asociadas).

## 2026-04-28 - Contexto de pago centralizado

- Se introduce `_build_payment_context()` en `views.py` para construir el contexto comun de todas las vistas de pago.
- Elimina duplicacion de logica entre `mesa_pedido`, `mesa_solicitar_cuenta`, `mesa_modal_pago`, `orden_procesar_pago`, `orden_pre_cuenta` y `terminal_modal_pago`.
- El contexto incluye: desglose IVA, propinas pagadas/sugeridas, totales, items pagados/pendientes, transacciones y metodos de pago activos.

## 2026-04-28 - Estructura de vista de pagos

- El orden de informacion en vista de mesas y cuenta es: Productos → Desglose → Pagos (tabla) → Pendiente de Pago.
- La tabla de pagos muestra columnas: Tipo | Forma de pago | Consumo | Propina | Total.
- El modal de pagos es para ingresar pagos, no para consultar historial. Se elimina el detalle de pagos realizados del modal.

## 2026-04-28 - Apertura y cierre de caja (Tarea 013)

- Los modelos CashRegister, CashSession y CashMovement se ubican en `apps/orders/`, junto a Transaction y PaymentMethod, dado que CashMovement tiene FK a Transaction y el flujo de pagos requiere CashSession abierta.
- Solo se permite 1 sesion abierta por caja. Si ya existe una sesion ABIERTA para una caja, no se puede abrir otra.
- Se permite cerrar una sesion con descuadre. Se registra `monto_cierre_declarado` y se calcula automaticamente `diferencia = monto_cierre_declarado - monto_cierre_calculado`. La diferencia queda registrada pero no bloquea el cierre.
- No se permite reabrir una sesion cerrada. Es definitiva. Si hubo error, se crea una nueva sesion.
- Los movimientos de caja son solo monetarios: INGRESO, EGRESO, AJUSTE. Se vinculan opcionalmente a una Transaction. No incluyen movimientos de inventario.
- Los pagos registrados via `register_transaction()` generan automaticamente un CashMovement tipo INGRESO vinculado a la CashSession correspondiente.
- No se puede registrar un pago sin una CashSession abierta para la caja compatible con el flujo de la orden.
- Se agregan permisos: `manage_cash_registers`, `open_cash_session`, `close_cash_session`.

## 2026-04-28 - Cuadratura detallada de caja (Tarea 013 — correcciones)

- **Modelo CashCloseDetail**: cuadratura individual por medio de pago con `monto_sistema`, `monto_declarado`, `diferencia` y `comentario` por medio. Unique por (cash_session, payment_method).
- **Comentario de diferencia por medio**: cada diferencia por medio de pago requiere un comentario especifico obligatorio en `CashCloseDetail.comentario`.
- **CashMovement.payment_method**: FK a PaymentMethod para trazabilidad del medio de cada movimiento. Movimientos automaticos heredan `payment_method` de la transaccion. Movimientos manuales INGRESO/EGRESO se asignan automaticamente a "Efectivo". AJUSTE requiere seleccion explicita de medio.
- **Signo de AJUSTE por radio**: el monto siempre es positivo. El signo se controla via radio "Credito (+)" / "Debito (-)" en la UI y la vista niega el monto si es debito antes de pasarlo al servicio. Eliminada la validacion de monto negativo en el servicio.
- **Propina incluida en CashMovement automatico**: `monto = transaction_amount + tip_amount`. El `payment_method` se hereda de la transaccion.
- **Flujo de cierre en 2 pasos**: (1) Pantalla de ingreso con boton "Revisar Cierre" → (2) Pantalla de revision readonly con botones "Modificar" y "Confirmar Cierre de Caja". Nueva vista `sesion_confirmar` (POST) que ejecuta `close_cash_session` solo al confirmar. Nueva URL `caja/sesion/<id>/confirmar/`.
- **Historial de cierres**: nueva vista `sesiones_cerradas` en `caja/cierres/`. Lista todas las sesiones CERRADA con tabla: caja, abierto/cerrado por, fechas, montos, diferencia, acceso a detalle.
- **Template tag `currency`**: ubicado en `apps/core/templatetags/currency.py` dentro de la app `apps.core` (registrada en INSTALLED_APPS). Filtros: `currency` (`$X.XXX`, sin decimales, separador de miles con punto) y `get_item` (acceso a diccionario por clave en templates).
- **Columnas ocultas por defecto**: en la pantalla de cierre, "Total sistema" y "Diferencia" estan ocultas con boton toggle unificado "Columnas" (icono eye/eye-slash).
- **Monto declarado por defecto = 0**: en la pantalla de ingreso de cierre, todos los inputs de monto declarado parten en 0. El cajero debe contar y declarar activamente.
- **Cuadratura general derivada**: `monto_cierre_declarado` general se calcula como suma de los montos declarados por medio de pago (backend). No es un input separado.
- **Apertura en breakdown Efectivo**: el `monto_apertura` de la sesion se suma al "Total sistema" del metodo Efectivo en el breakdown de cuadratura, tanto en pantalla como al crear CashCloseDetail.

- El orden de informacion en vista de mesas y cuenta es: Productos → Desglose → Pagos (tabla) → Pendiente de Pago.
- La tabla de pagos muestra columnas: Tipo | Forma de pago | Consumo | Propina | Total.
- El modal de pagos es para ingresar pagos, no para consultar historial. Se elimina el detalle de pagos realizados del modal.
