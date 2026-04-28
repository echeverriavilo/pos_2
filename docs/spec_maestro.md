# Spec Maestro - Gastropos

## 1. Proposito y alcance del producto

Gastropos es un sistema POS gastronomico para cafeterias, bares y locales de comida rapida. Su propuesta de valor es bajo costo de adopcion, operacion mobile-first, soporte para multiples flujos de venta e integracion flexible con hardware.

El sistema es:

- PWA;
- multitenant con aislamiento por tenant;
- server-rendered con HTMX;
- orientado a operaciones de pedidos, mesas, pagos, inventario y roles por local.

Alcance funcional actual:

- gestion de pedidos;
- gestion de mesas opcional;
- pagos totales y parciales;
- formas de pago por tenant;
- cajas, aperturas y cierres;
- inventario;
- catalogo de productos;
- roles y permisos por tenant;
- comandas, cocinas y barras operativas.

Restricciones de producto:

- debe funcionar bien en moviles;
- debe aislar completamente los datos por tenant;
- debe soportar operacion offline, pero el mecanismo completo sigue abierto;
- no se asume arquitectura distribuida.

## 2. Glosario esencial

- Tenant: unidad logica que representa un local.
- Flujo con mesas: operacion basada en mesas fisicas.
- Flujo rapido: operacion sin mesas, tipo barra o takeaway.
- Comanda: registro de productos enviados a preparacion.
- Pago parcial: pago incompleto de una orden.
- Abono: monto parcial aplicado a una orden.

## 3. Arquitectura general

### Estilo

- monolito modular;
- backend centrado en dominio;
- frontend server-rendered con HTMX;
- PostgreSQL como persistencia.

### Componentes

- Backend Django: logica de negocio, persistencia, validaciones y control de estados.
- Frontend Templates + HTMX: renderizacion e interaccion.
- Base de datos PostgreSQL: integridad estructural y persistencia.

### Flujo de interaccion

1. El usuario interactua con la UI.
2. HTMX o HTTP llama al backend.
3. El backend ejecuta logica en services.
4. Se persiste el nuevo estado.
5. El backend responde HTML parcial o completo.
6. La UI refleja el resultado.

### Autoridad de dominio

- El backend es la unica fuente de verdad.
- El frontend no toma decisiones de dominio.
- La base no contiene logica de negocio.

### Restricciones arquitectonicas

- No microservicios.
- No logica distribuida.
- No duplicacion de reglas.
- No signals para logica de negocio critica.
- No side-effects ocultos.

## 4. Multitenancy

### Estrategia

- aislamiento por `tenant_id` en todas las tablas relevantes;
- enforcement a nivel ORM y a nivel aplicacion.

### Resolucion de tenant

- el tenant se obtiene desde el subdominio;
- el middleware debe extraer subdominio, resolver tenant e inyectarlo en `request`.

### Reglas de acceso

- usuarios de tenant solo operan sobre su tenant;
- `platform_staff` puede operar sobre cualquier tenant, pero requiere logica explicita en backend;
- ninguna query de dominio debe ejecutarse sin tenant, salvo bypass controlado para `platform_staff`.

### Estado implementado

- existe middleware y contexto de tenant;
- los managers/querysets tenant-aware aplican filtros por tenant;
- el dominio base (`core`, `catalog`, `dining`, `orders`) ya esta adaptado al aislamiento.

## 5. Modelo de dominio

### Tenant

- `id: UUID`
- `slug: string unique`
- `nombre: string`
- `config_iva: decimal default 0.19`
- `config_flujo_mesas: boolean`
- `created_at: datetime`

### User

- `id: UUID`
- `email: string unique`
- `first_name: string`
- `last_name: string`
- `is_active: boolean`
- `is_staff: boolean`
- `is_superuser: boolean`
- `is_platform_staff: boolean`
- `pin_hash: string nullable`
- `pin_enabled: boolean`
- `date_joined: datetime`

Reglas:

- el tenant y rol operativo se resuelven via membership;
- `platform_staff` no tiene tenant fijo;
- el PIN es opcional y operativo;
- `get_short_name()` debe resolver nombre corto para UI.

### Membership

- `user: FK(User)`
- `tenant: FK(Tenant)`
- `role: FK(Role)`

Reglas:

- relacion operativa 1:1 user-tenant;
- define el rol operativo del usuario en ese tenant.

### Role

- `tenant: FK(Tenant)`
- `name: string`
- `description: text`
- `permissions: M2M(Permission, through RolePermission)`
- `created_at: datetime`

Reglas:

- nombre unico por tenant;
- roles base: administrador, cajero, garzon.

### Permission

- `codename: string unique`
- `description: text`

Permisos del sistema:

- `create_order`
- `add_item`
- `remove_item`
- `register_payment`
- `manage_inventory`
- `manage_users`
- `manage_tables`
- `manage_devices`

### RolePermission

- `role: FK(Role)`
- `permission: FK(Permission)`
- `active: boolean`
- `updated_at: datetime`

### Category

- `tenant: FK`
- `nombre: string`

### Product

- `tenant: FK`
- `category: FK`
- `nombre: string`
- `precio_bruto: decimal`
- `es_inventariable: boolean`
- `stock_actual: decimal`

### Ingredient

Entidad de catalogo para composicion de productos e inventario futuro.

### StockMovement

- `tenant: FK`
- `product: FK`
- `tipo: enum(INGRESO, AJUSTE, VENTA)`
- `cantidad: decimal`

### DiningTable

- `tenant: FK`
- `numero: string`
- `estado: enum(DISPONIBLE, OCUPADA, PAGANDO, RESERVADA)`

### Order

- `tenant: FK`
- `tipo_flujo: enum(MESA, RAPIDO)`
- `table: FK(DiningTable, nullable)`
- `estado: enum(ABIERTO, CONFIRMADO, PAGADO_PARCIAL, COMPLETADO, ANULADO)`
- `total_bruto: decimal`
- `propina_monto: decimal`

### OrderItem

- `order: FK(Order)`
- `product: FK(Product)`
- `cantidad: int`
- `precio_unitario_snapshot: decimal`
- `estado: enum(PENDIENTE, PREPARACION, ENTREGADO, ANULADO, PAGADO)`

Reglas:

- el tenant se fuerza desde la orden;
- el precio es inmutable una vez creado;
- un item en estado `PAGADO` no puede modificarse ni anularse.

### Transaction

- `tenant: FK`
- `order: FK(Order)`
- `monto: decimal`
- `tipo_pago: enum(TOTAL, ABONO, PRODUCTOS)`
- `payment_method: FK(PaymentMethod)`
- `tip_amount: decimal`

Reglas:

- toda transaccion debe indicar forma de pago;
- la propina evoluciona a nivel de pago/transaccion;
- mientras exista compatibilidad con implementacion previa, `Order.propina_monto` puede mantenerse como campo transitorio derivado o de compatibilidad.

### TransactionItem

- `transaction: FK(Transaction)`
- `order_item: FK(OrderItem)`
- `tenant: FK`

Regla:

- mantiene trazabilidad de que items se pagaron en cada transaccion.

### PaymentMethod

- `tenant: FK(Tenant)`
- `nombre: string`
- `activo: boolean`
- `orden: int`

Reglas:

- medios de pago base por defecto: efectivo, tarjeta debito, tarjeta credito y transferencia;
- cada tenant puede personalizar su catalogo de medios de pago.

### CashRegister

- `tenant: FK(Tenant)`
- `nombre: string`
- `soporta_flujo_mesa: boolean`
- `soporta_flujo_rapido: boolean`
- `activo: boolean`

### CashSession

- `tenant: FK(Tenant)`
- `cash_register: FK(CashRegister)`
- `opened_by: FK(User)`
- `closed_by: FK(User, nullable)`
- `opened_at: datetime`
- `closed_at: datetime nullable`
- `estado: enum(ABIERTA, CERRADA)`

Reglas:

- no existen movimientos operativos sin una `CashSession` abierta;
- cada apertura debe cerrarse con cuadratura.

### CashMovement

- `tenant: FK(Tenant)`
- `cash_session: FK(CashSession)`
- `transaction: FK(Transaction, nullable)`
- `tipo: enum(INGRESO, EGRESO, AJUSTE)`
- `monto: decimal`

### Dispositivo

- `tenant: FK`
- `nombre: string`

### KitchenBarStation

- `tenant: FK(Tenant)`
- `nombre: string`
- `tipo: enum(COCINA, BARRA)`
- `activo: boolean`
- `ocultar_en_listo: boolean`
- `ocultar_en_entregado: boolean`

Reglas:

- cada tenant puede tener cero, una o varias estaciones;
- los productos pueden mapearse a cocina o barra;
- el backend actual de dispositivos/comandas puede reutilizarse como infraestructura compatible durante la transicion.

## 6. Reglas de negocio

### Multitenancy

- toda operacion se asocia a un tenant;
- ninguna query de dominio debe ejecutarse sin tenant, salvo bypass controlado de `platform_staff`.

### Flujo con mesa

- abrir una mesa disponible crea una orden `ABIERTO`;
- una mesa ocupada implica orden activa;
- los productos se envian a preparacion inmediatamente al agregarse;
- si se agregan productos a una mesa `PAGANDO`, la mesa vuelve a `OCUPADA`.

### Flujo rapido

- la orden se crea `ABIERTO`;
- los productos no se envian a preparacion hasta pago total;
- el estado `CONFIRMADO` solo ocurre despues del pago total;
- la entrega completa la orden.

### Estados de Order

Estados validos:

- `ABIERTO`
- `CONFIRMADO`
- `PAGADO_PARCIAL`
- `COMPLETADO`
- `ANULADO`

Transiciones validas:

- Flujo mesa: `ABIERTO -> PAGADO_PARCIAL`, `ABIERTO -> COMPLETADO`, `PAGADO_PARCIAL -> COMPLETADO`
- Flujo rapido: `ABIERTO -> PAGADO_PARCIAL`, `PAGADO_PARCIAL -> CONFIRMADO`, `CONFIRMADO -> COMPLETADO`

### Orden activa en mesas

Se considera orden activa una orden en estado:

- `ABIERTO`
- `PAGADO_PARCIAL`
- `CONFIRMADO`

### Pagos

- una orden puede tener multiples transacciones;
- el total pagado no puede exceder el total de la cuenta;
- pago por productos solo aplica a `OrderItem` no pagados;
- un item pagado no puede modificarse ni anularse;
- un abono no modifica items, solo el saldo general;
- toda transaccion debe registrar forma de pago;
- no puede existir pago sin apertura de caja activa.

### Total de cuenta

- `total_cuenta = total_bruto + suma_propinas_de_pago`;
- el saldo pendiente se calcula contra `total_cuenta`;
- el pago total debe cubrir tambien las propinas aplicadas.

### Propina

- es opcional;
- opera por pago;
- sugerencia base: 10% del total;
- puede ser aceptada, rechazada o reemplazada por monto/porcentaje personalizado;
- el modelo exacto de persistencia puede pasar por una refactorizacion incremental desde la implementacion previa.

### Caja

- cada tenant puede tener multiples cajas;
- cada caja puede soportar flujo mesa, flujo rapido o ambos;
- toda operacion monetaria debe quedar asociada a una apertura de caja activa;
- cada apertura debe cerrarse con cuadratura.

### Inventario

- `stock_actual` solo cambia via `StockMovement`;
- flujo mesa: descuento al agregar producto;
- flujo rapido: descuento al confirmar pedido tras pago total;
- anulaciones deben revertir stock cuando corresponda.

### Anulacion

- no se pueden anular productos ya pagados;
- la anulacion debe recalcular la orden y revertir inventario si aplica.

### Dispositivos y comandas

- en flujo mesa, las comandas se generan al agregar productos;
- en flujo rapido, las comandas se generan al confirmar la orden;
- la asignacion a dispositivos respeta configuracion especifica, categoria, prioridad y dispositivo por defecto;
- no se deben generar comandas duplicadas para la misma combinacion item-dispositivo.

### Cocina y barra

- cada tenant puede operar cero, una o varias cocinas y/o barras;
- cada producto puede configurarse para una estacion de cocina o barra;
- la pantalla de estacion muestra pedidos `PENDIENTE`;
- la estacion puede mover items a `LISTO` y opcionalmente `ENTREGADO` segun configuracion tenant;
- los items pueden desaparecer de pantalla segun la politica configurada para esa estacion.

## 7. Invariantes

- toda entidad de dominio pertenece a un tenant;
- ninguna operacion de dominio se ejecuta sin tenant, salvo bypass controlado;
- una orden no puede estar `COMPLETADO` si el total pagado es menor al total de la cuenta;
- no puede existir pago o movimiento de caja sin `CashSession` abierta;
- un `OrderItem PAGADO` no cambia de estado;
- `stock_actual` solo cambia mediante `StockMovement`;
- en flujo rapido no puede existir `CONFIRMADO` sin pago total;
- una mesa `DISPONIBLE` no puede tener orden activa;
- una mesa `OCUPADA` o `PAGANDO` debe tener exactamente una orden activa.

## 8. Flujos operativos

### Flujo con mesa

1. Cliente llega a una mesa `DISPONIBLE`.
2. Garzon abre la mesa.
3. Mesa pasa a `OCUPADA`.
4. Se crea `Order` en `ABIERTO`.
5. Se agregan productos; cada adicion puede generar comanda inmediata.
6. Cliente solicita cuenta y la mesa puede pasar a `PAGANDO`.
7. Si se agregan productos desde `PAGANDO`, vuelve a `OCUPADA`.
8. Se reciben pagos totales o parciales, cada uno con forma de pago y propina opcional por pago.
9. Cada pago debe quedar asociado a una caja abierta.
10. Cuando la cuenta queda totalmente pagada, la orden se completa y la mesa vuelve a `DISPONIBLE`.

### Flujo rapido

1. Se crea `Order` en `ABIERTO`.
2. Se agregan productos.
3. Se registran pagos asociados a caja abierta, forma de pago y propina opcional por pago.
4. Con pago total, la orden pasa a `CONFIRMADO`.
5. Se generan comandas pendientes.
6. Cocina/barra opera los items en pantalla hasta `LISTO` o `ENTREGADO` segun configuracion.
7. La orden pasa a `COMPLETADO`.

### Pagos parciales

Tipos:

- por productos: marca items especificos como pagados;
- por monto: registra abono y reduce saldo sin afectar items.

### Cierre de cuenta

- el modulo de pagos debe mostrar subtotal, IVA, propina y total;
- el ticket/pre-cuenta debe actualizarse tras cada pago;
- la condicion de completado depende del flujo (`COMPLETADO` para mesa; `CONFIRMADO` como cierre de pago en rapido antes de entrega).

### Apertura y cierre de caja

1. El usuario abre una caja para un turno.
2. Todo pago o movimiento monetario se asocia a esa apertura.
3. La operacion del turno queda agrupada por caja y sesion.
4. El turno se cierra con cuadratura y resumen de movimientos.

## 9. Roles y permisos

### Administrador

Puede gestionar:

- configuracion del local;
- usuarios;
- catalogo;
- inventario;
- reportes financieros.

### Cajero

Puede gestionar:

- pagos;
- apertura y cierre de caja;
- transacciones parciales.

### Garzon

Puede gestionar:

- mesas;
- creacion de pedidos;
- adicion de productos;
- solicitud de pre-cuenta.

Restricciones:

- no puede anular productos pagados;
- no puede anular sin autorizacion cuando la configuracion no lo permite.

### Sistema de permisos

- cada tenant puede activar o desactivar permisos especificos por rol;
- las validaciones de tenant y permiso ocurren en services;
- `platform_staff` bypassa tenant, no permisos.

Permisos del tenant a extender:

- `manage_payment_methods`
- `manage_cash_registers`
- `open_cash_session`
- `close_cash_session`
- `view_reports`
- `manage_tenant_settings`
- `manage_kitchen_bar_stations`

Permisos de plataforma a extender:

- gestion global de tenants;
- gestion global de usuarios y reseteo de credenciales;
- acceso a logs y tickets de soporte.

## 10. Convenciones de implementacion

### Idioma y region

- codigo en ingles;
- comentarios y docstrings en espanol;
- mensajes de commit en espanol;
- timezone `America/Santiago`;
- locale `es_CL`.

### Estructura

Cada app usa:

- `models/`
- `services/`
- `selectors/`
- `tests/`

### Reglas de codigo

- codigo explicito, trazable a spec y sin ambiguedad;
- nombres de clases en PascalCase;
- funciones y variables en snake_case;
- no usar nombres genericos ambiguos;
- cada servicio representa una accion de negocio explicita;
- validar input, ejecutar logica y retornar resultado claro;
- docstrings en espanol para funciones relevantes;
- comentarios solo cuando explican reglas de negocio o logica no trivial;
- errores explicitos; no manejo silencioso;
- `try/except` solo con manejo claro.

### Git

- estrategia actual: trabajo directo sobre `main`;
- cada commit debe representar un cambio funcional coherente;
- no dejar codigo incompleto en `main`;
- no usar mensajes ambiguos.

## 11. Estrategia de testing

### Principio

Los tests validan:

- reglas de negocio;
- invariantes;
- flujos del sistema.

### Tipos

- unit tests para services y logica de negocio;
- integration tests para interaccion entre componentes y persistencia;
- tests UI/HTMX cuando una vista cambia comportamiento operativo.

### Cobertura obligatoria

- cada regla de negocio debe tener al menos un test;
- cada flujo definido debe estar cubierto;
- los escenarios criticos son obligatorios.

### Escenarios criticos

- apertura de mesa;
- multiples pedidos por mesa;
- cambio a `PAGANDO` y vuelta a `OCUPADA`;
- cierre de mesa;
- creacion de pedido rapido;
- pago completo y paso a preparacion;
- pago total, pago parcial por productos, pago parcial por monto, multiples pagos;
- propina sugerida, aceptada, rechazada y personalizada;
- generacion de comandas por dispositivo, categoria, prioridad y default;
- descuento de stock en flujo mesa y rapido.

### Naming

- `test_<accion>_<condicion>_<resultado>`

## 12. Restricciones y decisiones abiertas

### Restricciones vigentes

- no SPA;
- no frameworks JS adicionales;
- no logica de negocio en frontend;
- no microservicios;
- no signals para logica critica;
- no operaciones parciales en pagos, stock o transiciones.

### Decisiones abiertas

- modelo final de persistencia para propina por pago y compatibilidad con `Order.propina_monto`;
- estrategia definitiva offline para la PWA;
- driver y contrato final de impresion Web Bluetooth;
- alcance futuro de `Ingredient` y su integracion con descuentos de stock compuestos;
- posibles patrones HTMX avanzados, aun no habilitados como norma general;
- backlog PWA/Bluetooth/Offline fuera del MVP activo hasta nueva priorizacion.
