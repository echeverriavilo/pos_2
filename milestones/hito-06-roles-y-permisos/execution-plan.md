# Execution Plan — Hito 6: Roles y Permisos

## Fase 1: Modelo

- Validar modelo User existente
- Validar relación con Role

---

## Fase 2: Definición de Acciones

Definir conjunto explícito de acciones:

- CREATE_ORDER
- ADD_ITEM
- REMOVE_ITEM
- REGISTER_PAYMENT
- MANAGE_INVENTORY
- MANAGE_USERS
- MANAGE_TABLES

---

## Fase 3: Servicios de Autorización

Implementar:

- validate_tenant_access
- validate_role_permission

---

## Fase 4: Integración en Servicios

Modificar TODOS los services:

- DiningTable services
- Order services
- Payment services

Para incluir:

- validación de tenant
- validación de permisos

---

## Fase 5: Reglas por Rol

Implementar mapping:

### Admin
- acceso total

### Cajero
- REGISTER_PAYMENT

### Garzón
- CREATE_ORDER
- ADD_ITEM
- MANAGE_TABLES

---

## Fase 6: Platform Staff

- bypass de tenant
- NO bypass automático de permisos (debe evaluarse explícitamente)

---

## Fase 7: Testing

Tests obligatorios:

- acceso permitido por rol
- acceso denegado por rol
- aislamiento de tenant
- acceso platform_staff

---

## Fase 8: Validación

- todos los servicios protegidos
- no existen endpoints sin validación