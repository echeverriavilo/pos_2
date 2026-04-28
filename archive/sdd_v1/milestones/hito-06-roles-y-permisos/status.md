# Status — Hito 6: Roles y Permisos

## Estado General
**COMPLETADO** ✓

---

## Progreso

- Modelo: ✓
- Servicios auth: ✓
- Integración: ✓
- Roles base con permisos: ✓
- Testing: ✓

---

## Acceptance Criteria Verificado

✓ Modelo de usuario: tenant users + platform_staff
✓ Validación tenant para usuarios
✓ Platform staff bypass tenant
✓ Platform staff validación permisos
✓ Admin tiene todos los permisos
✓ Cajero: register_payment
✓ Garzón: manage_tables, create_order, add_item
✓ Enforcement en todos los servicios
✓ Aislamiento multitenancy
✓ 43 tests pasando

---

## Dependencias

- Hito 3 (Mesas)
- Hito 4 (Órdenes)
- Hito 5 (Pagos)

---

## Implementado

### Modelos
- `apps/core/models/permission.py` - Permission (codename, description)
- `apps/core/models/role_permission.py` - RolePermission (through) CON toggle active/inactivo
- `apps/core/models/role.py` - agregado ManyToManyField permissions

### Constantes
- `apps/core/constants/actions.py` - SystemActions

### Servicios de autorización
- `apps/core/services/auth.py` - validate_tenant_access, validate_role_permission

### Tenant Service actualizado
- `apps/core/services/tenant.py` - _seed_roles ahora asigna permisos automáticamente

### Servicios de personalización de roles (NUEVO)
- `apps/core/services/role.py` - RoleService CRUD completo:
  - create_role, update_role, delete_role
  - add_permission, remove_permission
  - toggle_permission, activate_permission, deactivate_permission
  - get_permissions, get_active_permissions, get_inactive_permissions
  - has_permission (con active_only)
- `apps/core/services/permission.py` - PermissionService

### Selectores
- `apps/core/selectors/role.py` - RoleSelector

### Migraciones
- 0002: Permission, RolePermission
- 0003: Permisos base (create_order, add_item, etc)
- 0004: Role permissions mapping
- 0005: RolePermission toggle (active, updated_at)

### Integración en servicios existentes
- `apps/core/services/order.py` - create_order, add_item, remove_item
- `apps/core/services/payment.py` - register_transaction
- `apps/core/services/table.py` - create_table, open_table, set_table_paying, reopen_table

### Tests
- 60 tests pasando

---

## Personalización por Tenant implementada

| Operación | Método |
|----------|--------|
| CRUD roles | RoleService.create_role, update_role, delete_role |
| Agregar permiso | RoleService.add_permission |
| Quitar permiso | RoleService.remove_permission |
| Toggle activo/inactivo | RoleService.toggle_permission |
| Activar | RoleService.activate_permission |
| Desactivar | RoleService.deactivate_permission |
| Listar activos | RoleService.get_active_permissions |
| Listar inactivos | RoleService.get_inactive_permissions |

---

## Riesgos

- Ninguno

---

## Bloqueos

- Ninguno