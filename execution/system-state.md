# System State

## Implemented Entities

- `Tenant` (UUID, slug/subdominio, config y timestamps).
- `Role` (ligado a tenant con carga base `administrador`, `cajero`, `garzón`).
- `Membership` (relación 1:1 user ↔ tenant + rol validando coherencia de tenant).
- `StaffTenantAccess` (permite a platform staff asignar accesos cruzados a tenants específicos).
- `CustomUser` extendido con PIN de 4 dígitos, bandera `is_platform_staff` y helpers para PIN y resoluciones de tenant/rol.

---

## Implemented Flows

- Creación de tenant por `TenantService.create_tenant`, que siembra roles y permanece en una transacción atómica.
- Autenticación operativa con email+password y opción de PIN rápido (hash, validación de 4 dígitos, habilitación/deshabilitación) sin reemplazar la contraseña principal.
- Resolución de tenant desde el subdominio mediante `TenantMiddleware` y `tenant_context`, exponiendo `request.tenant` y garantizando filtros por `tenant_id`.
- Enforcement multitenant por `TenantAwareManager`/`QuerySet` y constraints en la base de datos.

---

## Implemented States

- Tenant context disponible para toda request/middleware, habilitando la separación de datos por subdominio.
- Diferenciación entre usuarios operativos (tenant/rol obligatorio) y platform staff (pueden tener múltiples accesos) con flags específicas.
- PIN habilitado/deshabilitado de forma explícita (`set_pin`, `disable_pin`).

---

## Notes

- La base PostgreSQL `pos2` (usuario `pos2_ow`, contraseña `1234`) ya está utilizada en migraciones y pruebas (`./.venv/bin/python manage.py migrate` y `./.venv/bin/python -m pytest`).
