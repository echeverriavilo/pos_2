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
