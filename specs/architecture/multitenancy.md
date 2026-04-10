# Multitenancy

## Estrategia

- Aislamiento mediante tenant_id en todas las tablas

---

## Resolución de Tenant

- El tenant se obtiene desde el subdominio

Ejemplo:

- tenant1.app.com → tenant = tenant1

---

## Middleware

- obligatorio
- debe:
  - extraer subdominio
  - resolver tenant
  - inyectar tenant en request

---

## Reglas de acceso

### Usuarios de tenant

- solo pueden acceder a su tenant

### Platform staff

- pueden acceder a cualquier tenant (requiere lógica explícita en backend)

---

## Enforcement

- a nivel ORM (querysets filtrados)
- a nivel aplicación (validaciones)