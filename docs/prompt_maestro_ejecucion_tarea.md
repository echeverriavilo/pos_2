Tarea: `012`

Archivo de tarea: `docs/tareas/012_mejoras_pago_y_formas_pago.md`

Objetivo de esta ejecución: `Implementar la tarea 12 según el SDD vigente.`

In scope: `Solo lo definido en la tarea 12 y sus dependencias directas.`

Out of scope: `Cualquier definición no cerrada en la tarea o en el spec maestro.`

Tipo de trabajo principal: `backend y frontend`

Archivos o módulos foco: `apps/orders`, `apps/core`

Restricciones adicionales: `Si la persistencia exacta de propina por pago o las reglas de reversa/reporting requieren decisiones no cerradas, detenerse y preguntar.`

Validaciones obligatorias: `pytest del módulo de pagos y sus integraciones`

Contexto extra: `La tarea 12 extiende la 11.`

Trabaja esta tarea usando el SDD vigente del proyecto.

Antes de implementar:
1. Lee `AGENTS.md`.
2. Lee `docs/spec_maestro.md`.
3. Lee `docs/tareas/012_mejoras_pago_y_formas_pago.md`.
4. Lee solo la regla relevante en `.opencode/rules/`.

Durante la ejecución:
- ejecuta solo el alcance indicado;
- no inventes reglas de negocio, permisos ni transiciones;
- no uses `archive/sdd_v1/` como fuente primaria;
- si hay una ambigüedad material, detente y pregunta;
- respeta `services/`, `selectors/`, multitenancy, atomicidad y testing.

Al cerrar:
- resume qué cambiaste;
- indica qué validaste;
- indica pendientes o riesgos.