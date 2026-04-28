# Regla Frontend

## Modelo UI

- Frontend server-rendered con Django Templates.
- HTMX solo para interacciones parciales.
- Bootstrap local; no depender de CDN.

## Reglas

- El frontend representa estado; no lo inventa.
- Cada acción del usuario debe mapear a una operación backend explícita.
- No agregar lógica de negocio en JavaScript.
- Mantener compatibilidad mobile-first y desktop.
- No convertir el sistema en SPA ni introducir frameworks JS extra sin spec.

## HTMX permitido

- `hx-get`
- `hx-post`
- `hx-target`
- `hx-swap`

Si un flujo dinámico exige más complejidad, resolverla primero en backend y mantener la UI como representación.
