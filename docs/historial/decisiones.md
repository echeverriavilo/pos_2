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

- El total de pago del sistema es `total_bruto + propina_monto`.
- `total_pending` y el cambio de estado de pago se calculan contra ese total.

## 2026-04-17 - Propina sugerida por defecto

- Si la orden no tiene propina definida, la UI de pagos propone automaticamente el 10%.
- El usuario puede modificarla o eliminarla.

## 2026-04-17 - Flujos de cierre por tipo de orden

- En flujo mesa, el pago total habilita cierre hacia `COMPLETADO`.
- En flujo rapido, el pago total lleva a `CONFIRMADO` antes de la entrega final.

## 2026-04-28 - Reordenamiento del roadmap MVP

- La tarea de PWA/Bluetooth/Offline sale del tramo activo del MVP y pasa a backlog posterior como `xx_pwa_bluetooth_offline.md`.
- El roadmap activo continua con tareas 12 a 21 enfocadas en pagos, cajas, backoffice, cocina/barra, inventarios, reporteria, configuracion tenant y panel de plataforma.
- El `spec_maestro` se alinea con propina por pago, formas de pago tenant-aware, caja operativa y estaciones de cocina/barra.
