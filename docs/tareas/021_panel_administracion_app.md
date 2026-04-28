# 021 - Panel de administracion de la app

## Objetivo

Implementar un panel de administracion de plataforma para superadmins y staff.

## Contexto

Esta tarea introduce el backoffice de plataforma, separado del backoffice tenant, para gestionar tenants, usuarios y soporte global del sistema.

## Dependencias

- `018_configuracion_tenant.md`
- `019_configuracion_avanzada_roles_usuarios.md`
- `020_reestructuracion_menu_y_permisos.md`

## Reglas aplicables

- el acceso se restringe a superadmins y staff de plataforma;
- la gestion de plataforma debe distinguirse del backoffice tenant;
- las acciones de plataforma deben quedar auditables.

## Plan de implementacion

- crear panel de gestion de tenants y configuraciones;
- agregar gestion de usuarios, roles y regeneracion de contrasenas por tenant;
- agregar logs y tickets de soporte;

## Criterios de aceptacion

- existe un panel de plataforma para superadmins/staff;
- se pueden gestionar tenants y sus configuraciones;
- se pueden gestionar usuarios y credenciales por tenant;
- existen logs de errores/cambios y gestion de tickets de soporte;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: SLA y workflow de soporte;
- pendiente de definicion: granularidad de auditoria;
- esta tarea opera a nivel plataforma y no debe mezclarse con el backoffice tenant.
