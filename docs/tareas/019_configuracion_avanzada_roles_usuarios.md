# 019 - Configuracion avanzada de roles y usuarios

## Objetivo

Implementar vistas de gestion avanzada de roles, usuarios y permisos.

## Contexto

Esta tarea extiende la tarea 6 desde la capa de servicios/autorizacion hacia la administracion visual y operativa.

## Dependencias

- `006_roles_permisos_autorizacion.md`
- `014_vistas_crud_backoffice.md`

## Reglas aplicables

- las reglas de permisos siguen validandose en services;
- la gestion visual no puede debilitar el aislamiento por tenant;
- la administracion debe distinguir permisos de rol y estado del usuario.

## Plan de implementacion

- crear vistas de gestion de roles y usuarios;
- exponer configuracion de permisos por rol;
- integrar altas, ediciones y estados operativos de usuarios;

## Criterios de aceptacion

- existen vistas para gestionar roles, usuarios y permisos;
- los cambios de permisos quedan aplicados al dominio operativo;
- la administracion respeta tenant y permisos administrativos;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: matrices finas de permisos;
- esta tarea extiende la tarea 6, no reemplaza la capa de autorizacion existente.
