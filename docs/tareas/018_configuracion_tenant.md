# 018 - Configuracion del tenant

## Objetivo

Implementar las vistas y reglas de configuracion general por tenant, incluyendo una configuracion minima obligatoria antes de operar.

## Contexto

Cada tenant debe quedar operativo con una configuracion estandar al momento del alta y poder administrarla posteriormente.

## Dependencias

- `001_base_multitenancy_identidad.md`
- `014_vistas_crud_backoffice.md`

## Reglas aplicables

- cada tenant debe tener una configuracion minima antes de operar;
- el alta de tenant debe dejar una configuracion base estandar;
- la configuracion debe respetar tenant y permisos administrativos.

## Plan de implementacion

- definir vistas de configuracion general;
- establecer seed o inicializacion estandar del tenant;
- validar precondiciones minimas de operacion;

## Criterios de aceptacion

- existe una configuracion general editable por tenant;
- un tenant nuevo recibe configuracion base estandar;
- el sistema puede verificar si el tenant cumple minimos para operar;

## Validacion requerida

- `pytest`

## Estado

Pendiente

## Notas y resultados

- pendiente de definicion: checklist exacto de configuracion minima;
- pendiente de definicion: que parametros se consideran bloqueantes para operar.
