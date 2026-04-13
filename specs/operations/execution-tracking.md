# Execution Tracking

## Propósito

Esta carpeta (`execution/`) documenta el estado operativo del SDD en tiempo real. Los agentes deben leer y escribir en estos archivos para mantener trazabilidad sobre qué hito y tarea están activos, qué decisiones o errores existen y cómo evoluciona el sistema.

## Archivos clave y cuándo actualizarlos

### current-milestone.md

- Contiene el hito actual, la fase y el estado (`en progreso`, `validado`, `completado`).
- Se actualiza cuando:
  - se inicia un nuevo hito (el orchestrator escribe el nombre y fase)
  - se cambia de fase (por ejemplo, de análisis a ejecución)
  - se cierra el hito (marcar estado `completado` y limpiar la tarea activa)

### current-task.md

- Indica la tarea que se está ejecutando; incluye un `task id`, descripción y un campo `status` (`pending`, `in progress`, `completed`).
- Se actualiza antes de delegar a cualquier worker (poner `pending`), durante la ejecución (pasar a `in progress`) y después de que se validen tests/documentación (`completed`).
- Al cerrar un hito se debe limpiar (archivo vacío o comentario indicando que no hay tareas activas).

### system-state.md

- Resume entidades, flujos y configuraciones implementadas; debe reflejar la infraestructura actual (apps, DB, etc.).
- Se actualiza cada vez que se introducen nuevas entidades/módulos arquitectónicos o se ajusta la configuración del entorno.

### decisions-log.md y errors-log.md

- Registrar cada decisión afín al dominio (arquitectura, reglas nuevas, restricciones) y cada error relevante o bloqueo.
- Las entradas deben seguir el formato establecido en cada archivo (fecha, contexto, decisión/error, impacto, acciones).

## Reglas adicionales

- Ningún hito puede considerarse cerrado si `current-task.md` sigue mostrando una tarea activa.
- El orchestrator es responsable de sincronizar estos archivos antes y después de cada paso clave (Task Loop, finalización, cambio de hito).
- Los workers solo deben leer `current-*`; las escrituras corresponden al orchestrator o al backend-agent bajo indicación explícita.
