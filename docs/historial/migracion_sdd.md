# Migracion SDD v1 -> OpenCode

## Objetivo

Compactar el entorno SDD sin perder reglas de negocio, arquitectura ni criterios de testing, y dejar la estructura antigua archivada en `archive/sdd_v1/`.

## Mapa de equivalencia

| Origen | Destino nuevo | Estado |
| --- | --- | --- |
| `AGENTS.md` | `AGENTS.md` | reescrito |
| `specs/product/*.md` | `docs/spec_maestro.md` | fusionado |
| `specs/architecture/*.md` | `docs/spec_maestro.md` | fusionado |
| `specs/domain/*.md` | `docs/spec_maestro.md` | fusionado |
| `specs/engineering/*.md` | `docs/spec_maestro.md` y `.opencode/rules/*.md` | fusionado |
| `specs/glossary.md` | `docs/spec_maestro.md` | fusionado |
| `agents/policies/*.md` | `.opencode/rules/00_core.md`, `30_testing.md`, `40_review.md` | fusionado |
| `agents/workers/*.md` | `.opencode/rules/*.md` | fusionado |
| `agents/orchestrator/*` | `.opencode/rules/00_core.md` | fusionado parcial |
| `execution/decisions-log.md` | `docs/historial/decisiones.md` | fusionado |
| `execution/system-state.md` | `docs/spec_maestro.md` | fusionado |
| `execution/current-task.md` | sin reemplazo permanente | descartado |
| `execution/current-milestone.md` | sin reemplazo permanente | descartado |
| `execution/error-log.md` | sin reemplazo permanente | archivado |
| `execution/errors-log.md` | sin reemplazo permanente | archivado |
| `milestones/hito-*` | `docs/tareas/*.md` | fusionado |
| `skills/*` | se mantiene fuera del nucleo SDD | conservado |

## Criterios aplicados

- Se conserva toda regla material del dominio.
- Se elimina duplicacion literal entre specs y prompts.
- Se eliminan logs de sesion como dependencia operativa.
- La configuracion de OpenCode se define en `opencode.json` en la raiz, porque es la ubicacion compatible con la documentacion oficial; `.opencode/` se usa para reglas modulares.

## Inventario resumido

### Fusionados

- `specs/`
- partes utiles de `agents/`
- partes persistentes de `execution/`
- contenido estructural de `milestones/`

### Archivados

- `agents/`
- `execution/`
- `milestones/`
- `specs/`

### Conservados fuera del nucleo

- `skills/`
- codigo fuente y assets actuales

## Validacion esperada

- un agente nuevo puede iniciar con `AGENTS.md`;
- el dominio canonico vive en `docs/spec_maestro.md`;
- cada hito relevante existe como tarea unica en `docs/tareas/`;
- la estructura anterior queda disponible en `archive/sdd_v1/` mientras se valida la migracion.
