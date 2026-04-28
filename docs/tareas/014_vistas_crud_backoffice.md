# 014 - Vistas CRUD de backoffice

## Objetivo

Implementar vistas de gestion para las entidades operativas del tenant, incluyendo productos, categorias, roles, usuarios y formas de pago.

## Contexto

Esta tarea introduce el backoffice tenant para administrar catalogo, usuarios y configuraciones operativas desde la UI.

## Dependencias

- `002_catalogo_inventario_base.md`
- `006_roles_permisos_autorizacion.md`
- `012_mejoras_pago_y_formas_pago.md`

## Reglas aplicables

- las vistas deben respetar permisos por rol;
- toda operacion CRUD debe respetar el aislamiento por tenant;
- la UI debe apoyarse en services y no introducir logica de negocio propia.

## Plan de implementacion

- crear vistas, formularios y listados para entidades operativas del tenant;
- integrar validaciones de permisos y tenant;

## Criterios de aceptacion

- existen vistas CRUD operativas para las entidades definidas;
- las operaciones respetan permisos y tenant;
- los cambios realizados desde la UI persisten correctamente;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: mapa exacto de vistas;
- pendiente de definicion: filtros, busquedas y UX detallada por modulo.
