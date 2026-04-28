# 007 - Shell PWA y autenticacion

## Objetivo

Establecer el layout base, navegacion, feedback visual y autenticacion server-rendered del producto.

## Contexto

La tarea crea el cascaron de la aplicacion y deja rutas operativas para moverse entre modulos.

## Dependencias

- `001_base_multitenancy_identidad.md`

## Reglas aplicables

- Bootstrap local;
- frontend server-rendered;
- mobile-first;
- no SPA ni login dependiente de templates autenticados.

## Plan de implementacion

- instalar Bootstrap e iconos localmente;
- crear `base.html` con sidebar responsivo y toasts;
- agregar dashboard y placeholders de modulos;
- implementar login y logout personalizados;
- verificar flujo completo de autenticacion.

## Criterios de aceptacion

- layout base funcional;
- sidebar responsivo;
- toasts visibles;
- navegacion entre modulos;
- login y logout operativos;
- compatibilidad movil y escritorio.

## Validacion requerida

- `python manage.py check`
- `pytest`

## Estado

Completado

## Notas y resultados

- el sistema usa Bootstrap local y login propio en `/login/`;
- `CustomUser.get_short_name()` soporta la UI autenticada.
