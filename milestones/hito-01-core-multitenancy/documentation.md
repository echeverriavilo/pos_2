# Documentación — Hito 01: Core Multitenancy

## Objetivo del hito

Establecer la base multitenant del producto: modelo de tenants, usuarios autenticados con PIN opcional, roles dinámicos por tenant y aislamiento estricto por columna `tenant_id`, todo respaldado por migraciones y pruebas.

## Artefactos generados

- Aplicación `apps.core` con los modelos `Tenant`, `Role`, `Membership`, `StaffTenantAccess` y `CustomUser` (PIN de 4 dígitos, `is_platform_staff`).
- Middleware `TenantMiddleware` + contexto thread-local `tenant_context` que resuelven el tenant actual desde el subdominio y lo exponen en `request.tenant`.
- Servicios `TenantService` y `UserService` para crear tenants, sembrar roles base (`administrador`, `cajero`, `garzón`) y gestionar usuarios/platform staff.
- `TenantAwareManager` y `QuerySet` que aplican filtros automáticos por tenant actual.
- Documentación en `milestones/hito-01-core-multitenancy/status.md`, `execution/system-state.md`, logs y este archivo.
- Suite de pruebas en `apps/core/tests/test_models.py` y migraciones iniciales (`apps/core/migrations/0001_initial.py`).

## Configuración requerida

1. Crear un archivo `.env` en la raíz con al menos estas variables (puede ampliarse según el entorno):

   ```env
   DJANGO_SECRET_KEY=algo-seguro
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   POSTGRES_DB=pos2
   POSTGRES_USER=pos2_ow
   POSTGRES_PASSWORD=1234
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   TENANT_DEFAULT_DOMAIN=localhost
   ```

2. La base de datos PostgreSQL `pos2` ya debe existir y el usuario `pos2_ow` debe tener permisos. No se permite SQLite.

3. Instalar dependencias dentro del entorno virtual (se definió `.venv` en esta sesión): `./.venv/bin/pip install -r requirements.txt`.

## Cómo verificar el hito

- Aplicar migraciones: `./.venv/bin/python manage.py migrate`.
- Ejecutar pruebas: `./.venv/bin/python -m pytest`.
- Verificar que `TenantService.create_tenant` siembra los roles base y que `CustomUser` expone `tenant`/`role` correctamente (ya cubierto por tests).

## Flujos clave documentados

1. **Creación de tenant**: se invoca `TenantService.create_tenant`, se crea el tenant, se siembran los roles base y se retorna la entidad.
2. **Asignación de usuario operativo**: `UserService.create_tenant_user` crea el usuario con email/password y una `Membership` que lo asocia a un tenant+rol.
3. **Staff de plataforma**: `UserService.create_platform_staff` crea usuarios con `is_platform_staff=True` y `StaffTenantAccess` para dar visibilidad multi-tenant sin violar el aislamiento.
4. **Autenticación**:
   - Email/password via Django auth (`CustomUserManager`).
   - PIN operativo (4 dígitos) con `CustomUser.set_pin`/`check_pin`: el PIN es opcional, se guarda hasheado y no reemplaza el password.
5. **Aislamiento multitenant**: `TenantMiddleware` lee el subdominio, resuelve el tenant, lo inyecta en `request` y `tenant_context`; `TenantAwareManager` limita automáticamente las consultas.

## Notas adicionales

- Las migraciones en el commit inicial ya crean todos los modelos y relaciones.
- Cuanto antes se habilite el despliegue con subdominios (p.ej. `tenant1.pos.example.com`), se podrá aprovechar el middleware actual.
- Las pruebas actuales cubren autenticación, PIN y aislamiento básico; conviene ampliar más adelante con intengraciones de usuarios y permisos.
