# 001 - Base multitenancy e identidad

## Objetivo

Establecer la base del sistema: proyecto Django operativo, PostgreSQL, multitenancy por subdominio, usuarios autenticados, roles y aislamiento por tenant.

## Contexto

Esta tarea define el arranque del dominio `core` y la infraestructura base que todas las apps reutilizan.

## Dependencias

- ninguna

## Reglas aplicables

- todo dato operativo se aisla por tenant;
- `platform_staff` requiere bypass explicito;
- autenticacion principal en backend Django;
- comentarios y docstrings en espanol.

## Plan de implementacion

- crear `Tenant`, `CustomUser`, `Role`, `Membership` y `StaffTenantAccess`;
- configurar PostgreSQL y variables de entorno;
- resolver tenant por subdominio con middleware/contexto;
- sembrar roles base por tenant;
- agregar soporte de PIN operativo;
- cubrir autenticacion y aislamiento con tests.

## Criterios de aceptacion

- el proyecto Django corre sin errores;
- PostgreSQL queda configurado;
- existen modelos base de tenant, usuario y roles;
- un usuario puede autenticarse;
- un usuario pertenece a un tenant;
- no es posible acceder a datos de otro tenant;
- existen tests de autenticacion y aislamiento;
- migraciones aplicadas y tests verdes.

## Validacion requerida

- `python manage.py check`
- `pytest`

## Estado

Completado

## Notas y resultados

- core multitenant implementado;
- PIN de 4 digitos soportado;
- tenant middleware y managers tenant-aware operativos.
