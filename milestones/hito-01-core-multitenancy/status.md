# Status — Hito 01

Estado: en progreso (infraestructura del core establecida)

## Avances clave

- El proyecto Django ya corre conectado a PostgreSQL (`pos2`, usuario `pos2_ow`, contraseña 1234) y se documentó cómo calibrar las variables de entorno en `grastro/settings.py`.
- Se introdujeron los modelos base (`Tenant`, `CustomUser`, `Role`, `Membership`, `StaffTenantAccess`) con los constraints necesarios para forzar aislamiento por `tenant_id` y el middleware/servicios para resolver el tenant por subdominio.
- El `CustomUser` soporta PIN de 4 dígitos (hash, validaciones, habilitación/deshabilitación) sin reemplazar la autenticación principal.
- Se implementaron pruebas que validan la siembra de roles base, la relación usuario-tenant, las validaciones de PIN y la filtración automática por tenant.
- Las migraciones iniciales se generaron y aplicaron exitosamente; `./.venv/bin/python -m pytest` pasa con la base Postgres.
