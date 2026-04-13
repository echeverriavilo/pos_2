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

- Fecha: 2026-04-13
  - Contexto: Hito 3 trabaja sobre mesas y prepara el motor de órdenes, por lo que hace falta garantizar la definición de un pedido activo y dejar una base organizada para el próximo hito.
  - Decisión: conceptuar “order activo” como los estados ABIERTO, PAGADO_PARCIAL y CONFIRMADO, implementar el servicio canónico `orders.services.create_order_for_table` y documentar que en hito 4 se requerirá un concepto de “OrderBatch / Comanda” más completo.
  - Justificación: el flujo de mesas debe garantizar invariantes (mesa DISPONIBLE sin pedido, OCUPADA/PAGANDO con pedido único) y el hito 4 extenderá el modelo hacia órdenes/comandas; separar la responsabilidad en un servicio asegura consistencia inmediata y flexibilidad futura.
  - Impacto: la mesa delega en el servicio de órdenes para crearlas, la definición de estados activos se reutiliza en selectores y servicios de mesas, y queda registrada la necesidad futura de un modelo OrderBatch/Comanda para el hito 4.
