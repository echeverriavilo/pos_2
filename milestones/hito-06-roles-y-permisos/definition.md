# Definition — Hito 6: Roles y Permisos

## Entidades

### User

- email
- password
- tenant: FK(Tenant, nullable)
- role: FK(Role, nullable)
- is_superuser: boolean
- is_platform_staff: boolean
- pin: nullable

---

### Role

- definido por tenant
- representa conjunto de permisos

---

## Conceptos

### Contexto de Usuario

Cada operación debe recibir:

- user
- tenant (implícito o explícito)

---

## Operaciones de Dominio

### validate_tenant_access(user, tenant)

- valida:
  - user.tenant == tenant
  - OR user.is_platform_staff

---

### validate_role_permission(user, action)

- valida si el rol permite la acción

---

## Acciones del Sistema (abstractas)

Ejemplos:

- create_order
- add_item
- register_payment
- manage_inventory
- manage_users

---

## Reglas

- validación debe ocurrir en services
- no usar lógica en views
- no confiar en frontend

---

## Dependencias

- User
- Tenant
- Todos los servicios existentes (integración)