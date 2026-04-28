# Hito 01 — Core Multitenancy

## Objetivo

Establecer la base del sistema:

- multitenancy con aislamiento por tenant_id
- autenticación de usuarios
- estructura base de entidades

---

## Dominio

### Tenant

- Representa un local gastronómico
- Un tenant = un local

---

### User

- Pertenece a un solo tenant
- Usa el sistema de autenticación de Django

---

## Roles

- Sistema obligatorio en este hito
- Roles dinámicos por tenant
- Cada tenant puede definir sus propios roles
- Debe existir una carga inicial estándar

Tipos de usuario:

- Usuario de tenant (operativo)
- Superusuario del sistema (admin/soporte, fuera del tenant)

---

## Entidades incluidas

- Tenant
- User (custom user)
- Role
- Membership (relación user ↔ tenant)
- (sin location, eliminado por inconsistencia con dominio actual)

---

## Multitenancy

- Estrategia: columna tenant_id
- Aislamiento obligatorio:
  - a nivel ORM
  - a nivel base de datos (constraints)

---

## Autenticación

- Base: Django auth

Métodos:

- email + password
- autenticación rápida mediante PIN (para operación en POS)

Reglas:

- PIN asociado a usuario
- PIN no reemplaza autenticación principal
- uso enfocado a operación interna

---

## Flujo mínimo

- crear tenant
- crear usuario
- asignar usuario a tenant
- autenticación
- acceso a contexto aislado

---

## Alcance

Incluye:

- modelos base
- autenticación
- aislamiento de datos
- migraciones
- tests

---

## Fuera de alcance

Todo lo definido en siguientes hitos:

- catálogo
- inventario
- mesas
- órdenes
- pagos

---

## Resultado esperado

Sistema base funcional que permite:

- crear tenants
- gestionar usuarios
- autenticarse
- operar con aislamiento completo por tenant