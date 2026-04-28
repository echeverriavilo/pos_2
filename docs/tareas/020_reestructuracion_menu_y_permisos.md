# 020 - Reestructuracion de menu y permisos

## Objetivo

Validar el mapa de vistas e implementar logica de permisos y roles en vistas y menu.

## Contexto

Esta tarea ordena la navegacion general del producto una vez existan las vistas principales del backoffice tenant.

## Dependencias

- `014_vistas_crud_backoffice.md`
- `018_configuracion_tenant.md`
- `019_configuracion_avanzada_roles_usuarios.md`

## Reglas aplicables

- el menu debe reflejar permisos efectivos del usuario;
- las vistas deben validar acceso incluso si no son visibles en el menu;
- la estructura de navegacion debe ser consistente con el mapa de vistas vigente.

## Plan de implementacion

- validar y consolidar el mapa de vistas;
- aplicar visibilidad condicional en menu;
- reforzar validaciones de acceso en vistas;

## Criterios de aceptacion

- el menu refleja el rol y permisos del usuario;
- las vistas ocultas por permisos no quedan accesibles por URL sin validacion;
- la navegacion general es coherente con los modulos implementados;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: arbol final del menu;
- depende del mapa de vistas resultante de las tareas 14, 18 y 19.
