# Acceptance Criteria — Hito 6: Roles y Permisos

## Objetivo

Implementar control de acceso basado en roles, asegurando que todas las operaciones del sistema respeten:

- permisos por rol
- aislamiento por tenant
- excepciones para platform_staff

---

## Modelo de Usuario

- Usuarios pueden ser:
  - tenant users (con tenant)
  - platform_staff (sin tenant)

---

## Reglas de Acceso

### Usuarios de Tenant

- Solo pueden operar sobre su tenant
- Deben tener un rol asignado

---

### Platform Staff

- Pueden operar sobre cualquier tenant
- No están restringidos por tenant_id
- Requieren validación explícita en servicios

---

## Roles Base

### Administrador

Puede:

- gestionar catálogo
- gestionar inventario
- gestionar usuarios
- acceder a reportes

---

### Cajero

Puede:

- registrar pagos
- gestionar transacciones

---

### Garzón

Puede:

- gestionar mesas
- crear órdenes
- agregar productos

Restricciones:

- no puede modificar ni anular productos pagados

---

## Enforcement

- Todas las operaciones críticas deben validar:
  - rol
  - tenant
  - permisos

---

## Restricciones

- No se permite acceso implícito
- No se permite bypass de validaciones en services

---

## Consistencia

Debe cumplirse:

- ningún usuario accede a datos de otro tenant (excepto platform_staff)
- todas las acciones pasan por validación de permisos