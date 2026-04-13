# Decisions Log

## Entry Format

- Fecha
- Contexto
- Decisión
- Justificación
- Impacto

---

## Entries

- Fecha: 2026-04-10
  - Contexto: Hito 01 exige aislamiento por tenant_id, autenticación operativa y soporte para staff de plataforma.
  - Decisión: crear el dominio `apps.core` con modelos `Tenant`, `Role`, `Membership`, `StaffTenantAccess` y `CustomUser`; resolver tenant por subdominio con middleware/tenant_context y forzar filtros adicionales en managers.
  - Justificación: el sistema debe asegurar aislamiento a nivel ORM y base de datos, mientras que los usuarios de soporte necesitan acceso controlado a múltiples tenants.
  - Impacto: las consultas quedan automáticamente limitadas por el tenant actual, los roles base (`administrador`, `cajero`, `garzón`) se siembran en la creación de tenant y queda soportado el login rápido por PIN sin comprometer la seguridad general.

- Fecha: 2026-04-12
  - Contexto: Hito 02 presentó el catálogo e inventario tenant-aware y necesitaba garantizar que el stock se mantuviera consistente para cada tenant.
  - Decisión: crear los modelos `Category`, `Product`, `Ingredient` y `StockMovement` con `TenantAwareManager`, implementar `InventoryService` con métodos separados por tipo de movimiento (ingreso/ajuste/venta) y mantener `Product.stock_actual` actualizado en transacciones atómicas, evitando stock negativo en productos inventariables.
  - Justificación: se requería un histórico confiable de movimientos, consultas rápidas al stock actual sin cálculos dinámicos y respeto al aislamiento por tenant.
  - Impacto: se documenta el flujo de inventario, se prepara la infraestructura para futuros hitos y se mantiene la consistencia entre movimientos y el stock persistido.

- Fecha: 2026-04-13
  - Contexto: Hito 3 formalizó la relación entre mesas y órdenes, con nuevas apps `dining` y `orders` que integran selectores, servicios y flujo de estados.
  - Decisión: conceptuar “order activo” como los estados ABIERTO, PAGADO_PARCIAL y CONFIRMADO, delegar la creación de órdenes a `orders.services.create_order_for_table`, y dejar documentadas las invariantes/responsabilidades del servicio de mesas (estado de mesa vs. orden) para facilitar el OrderBatch/Comanda del hito 4.
  - Justificación: mantener la propiedad de invariantes en `DiningTableService` y separar la creación de órdenes permite escalar el flujo hacia el motor de órdenes sin mezclar responsabilidades.
  - Impacto: la infraestructura queda organizada para el próximo hito, los selectores y servicios comparten la definición de estados activos y se documenta la necesidad futura de un modelo OrderBatch/Comanda.

- Fecha: 2026-04-12
  - Contexto: Hito 2 definió catálogo e inventario y necesitaba asegurar que el stock se mantuviera consistente por tenant y con históricos de movimientos.
  - Decisión: crear los modelos `Category`, `Product`, `Ingredient` y `StockMovement` con `TenantAwareManager`, implementar `InventoryService` con métodos separados por tipo de movimiento (ingreso, ajuste, venta) y mantener `Product.stock_actual` actualizado en transacciones, bloqueando stock negativo cuando corresponda.
  - Justificación: el inventario debe consultar fácilmente `stock_actual` sin cálculos dinámicos y los movimientos deben quedar registrados en un histórico verificable por tenant.
  - Impacto: se garantiza aislamiento de tenants en el catálogo/inventario, se documenta la necesidad de transacciones atómicas y se prepara el terreno para usar `InventoryService` en hitos futuros.

- Fecha: 2026-04-13
  - Contexto: Hito 3 formalizó la relación entre mesas y órdenes, además de crear las apps `dining` y `orders` necesarias para sostener la lógica.
  - Decisión: registrar en el log la creación de las apps `dining` y `orders`, el servicio `create_order_for_table` y los selectores que filtran mesas/órdenes activas; documentar la lista de estados válidos y las invariantes de `DiningTableService`.
  - Justificación: al mover orden explícitamente a `orders.services`, se facilita la evolución del motor de órdenes en el hito 4 y se mantiene la separación de responsabilidades entre servicios y selectores.
  - Impacto: la infraestructura queda organizada para el próximo hito y el log ya refleja las decisiones clave que acompañan a las nuevas apps.
