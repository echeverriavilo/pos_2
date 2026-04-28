# 006 - Roles, permisos y autorizacion

## Objetivo

Implementar control de acceso basado en roles y permisos dentro de los servicios del dominio.

## Contexto

La tarea completa la capa de autorizacion del core y la integra con mesas, ordenes y pagos.

## Dependencias

- `001_base_multitenancy_identidad.md`
- `004_motor_ordenes_y_items.md`
- `005_pagos_transacciones.md`

## Reglas aplicables

- las validaciones de acceso ocurren en services;
- `platform_staff` bypassa tenant, no permisos;
- los permisos base deben sembrarse para roles iniciales.

## Plan de implementacion

- crear `Permission` y `RolePermission`;
- definir acciones del sistema;
- implementar `validate_tenant_access` y `validate_role_permission`;
- integrar validacion en servicios existentes;
- cubrir permisos por rol y casos `platform_staff`.

## Criterios de aceptacion

- existen permisos explicitos del sistema;
- los roles base quedan asociados a permisos;
- las operaciones del dominio validan tenant y permiso;
- la excepcion de `platform_staff` funciona solo para tenant;
- los tests cubren autorizacion e integracion.

## Validacion requerida

- `pytest`

## Estado

Completado

## Notas y resultados

- todos los servicios criticos reciben `user`;
- se corrigio la siembra de permisos para roles base.
