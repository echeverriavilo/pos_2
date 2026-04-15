# System State

## Implemented Entities

- `Tenant` (UUID, slug/subdominio, config y timestamps).
- `Role` (ligado a tenant con carga base `administrador`, `cajero`, `garzón`).
- `Membership` (relación 1:1 user ↔ tenant + rol validando coherencia de tenant).
- `StaffTenantAccess` (permite a platform staff asignar accesos cruzados a tenants específicos).
- `CustomUser` extendido con PIN de 4 dígitos, bandera `is_platform_staff` y helpers para PIN y resoluciones de tenant/rol.
- **[Hito 06]** `Permission`: permisos del sistema (codename único).
- **[Hito 06]** `RolePermission`: tabla pivot role-permission.

---

## Implemented Flows

- Creación de tenant por `TenantService.create_tenant`, que inmue roles y permanece en una transacción atómica.
- Autenticación operativa con email+password y opción de PIN rápido (hash, validación de 4 dígitos, habilitación/deshabilitación) sin reemplazar la contraseña principal.
- Resolución de tenant desde el subdominio mediante `TenantMiddleware` y `tenant_context`, exponiendo `request.tenant` y garantizando filtros por `tenant_id`.
- Enforcement multitenant por `TenantAwareManager`/`QuerySet` y constraints en la base de datos.

---

## Implemented States

- Tenant context disponible para toda request/middleware, habilitando la separación de datos por subdominio.
- Diferenciación entre usuarios operativos (tenant/rol obligatorio) y platform staff (pueden tener múltiples accesos) con flags específicas.
- PIN habilitado/deshabilitado de forma explícita (`set_pin`, `disable_pin`).

---

## Additional Entities

- `Category`, `Product`, `Ingredient` y `StockMovement` con managers tenant-aware y `InventoryService`.
- `DiningTable` con estado/tenant filtering, selectors y servicios de transición.
- `Order` y `OrderItem` mínimos con estados activos y servicios de creación/add/remove.
  - `OrderItem` ahora fuerza tenant desde `order`, mantiene `precio_unitario_snapshot` inmutable y registra estados del flujo para respetar las invariantes del hito 4.
  - `OrderItem` entra a estado `PAGADO` tras pago por productos, volviéndose completamente inmutable (sin `update()` ni `delete()`).
- **[Hito 05]** `Transaction`: registra transacciones de pago (TOTAL, ABONO, PRODUCTOS) con tenant directo para multitenancy, monto y relación a Order.
- **[Hito 05]** `TransactionItem`: asociación explícita entre Transaction y OrderItem para trazabilidad de qué items fueron pagados en qué transacción, con tenant directo.

---

## Implemented Services

- `TenantService`: crea tenants, inmue roles base y mantiene transacciones atómicas.
- `InventoryService`: registra ingresos/ajustes/ventas y actualiza `Product.stock_actual` sin permitir stock negativo.
- `DiningTableService`: gestiona `create_table`, `open_table`, `set_table_paying` y `reopen_table` manteniendo invariantes.
- `create_order_for_table`: servicio canónico en `orders.services` para crear órdenes de mesa.
  - `orders.services`: ahora expone `create_order`, `add_item`, `remove_item`, `recalculate_total` y `transition_order_state`, junto a selectores de órdenes e ítems por tenant/mesa, con docstrings en español y validaciones por flujo (mesa vs. rápido).
- **[Hito 05]** `register_transaction`: servicio principal que crea transacciones de pago con validaciones de flujo, estado de orden, y saldo pendiente.
- **[Hito 05]** `apply_payment_to_items`: marca ítems como PAGADO y crea asociaciones TransactionItem para pago por productos.
- **[Hito 05]** `update_order_payment_state`: calcula total pagado acumulado y dispara transiciones de estado (ABIERTO → PAGADO_PARCIAL/CONFIRMADO/COMPLETADO).
- **[Hito 05]** `TransactionSelector`: selectors para listar pagos por orden, calcular totales pagado/pendiente.
- **[Hito 06]** `validate_tenant_access`: valida acceso al tenant (bypass para platform_staff).
- **[Hito 06]** `validate_role_permission`: valida permiso del rol.

---

## Constants

- **[Hito 06]** `SystemActions`: create_order, add_item, remove_item, register_payment, manage_inventory, manage_users, manage_tables.

---

## Services con Auth Integration

Todos los servicios reciben ahora parámetro `user` y validan:

- `apps/orders/services/order.py`: create_order, add_item, remove_item, create_order_for_table
- `apps/orders/services/payment.py`: register_transaction
- `apps/dining/services/table.py`: create_table, open_table, set_table_paying, reopen_table

---

## Infrastructure Notes

- Apps `core`, `catalog`, `dining` y `orders` registradas en `INSTALLED_APPS` y con migraciones aplicadas.
- PostgreSQL `pos2` con usuario `pos2_ow` sigue siendo la base activa (`manage.py migrate`, `python -m pytest`).

---

## Notes

- La base PostgreSQL `pos2` (usuario `pos2_ow`, contraseña `1234`) ya está utilizada en migraciones y pruebas.
- Hito 06: 43 tests pasando.
