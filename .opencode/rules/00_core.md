# Regla Core

## Orden de lectura

1. Leer `AGENTS.md`.
2. Leer `docs/spec_maestro.md` si la tarea toca dominio, arquitectura o criterios de negocio.
3. Leer el archivo relevante en `docs/tareas/` si existe.
4. Leer solo la regla de rol necesaria para la tarea actual.

## Reglas operativas

- `docs/spec_maestro.md` es la fuente canónica del sistema.
- No usar `archive/sdd_v1/` como fuente primaria; solo sirve de respaldo histórico.
- No inferir reglas de negocio, permisos o transiciones si la spec no las define.
- Si dos reglas parecen entrar en conflicto, preferir la formulación más específica.
- Si la ambigüedad cambia comportamiento de dominio, detenerse y pedir aclaración.
- Toda decisión importante debe ser trazable a spec o a `docs/historial/decisiones.md`.
- No introducir nuevas capas documentales paralelas al SDD canónico.

## Qué no hacer

- No reactivar logs de sesión dentro del repo.
- No recrear orquestadores documentales.
- No duplicar reglas de negocio en prompts de rol.
