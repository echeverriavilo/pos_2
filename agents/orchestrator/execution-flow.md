# Orchestrator Execution Flow

## Step 0: Load Context

- Leer:
  - /execution/current-milestone.md
  - /milestones/<hito>/definition.md
  - /milestones/<hito>/tasks.md
  - /milestones/<hito>/acceptance.md
  - /execution/system-state.md

- Verificar y, si corresponde, escribir en:
  - /execution/current-task.md (tarea activa o limpieza)
  - /execution/current-milestone.md (hito activo y fase)
  - /execution/system-state.md (cambios de arquitectura recientes)

---

## Step 1: Analysis Phase

- Analizar estado del sistema
- Analizar progreso del hito

---

## Step 2: Scope Definition

- Determinar:
  - entidades afectadas
  - módulos involucrados
  - límites del hito

---

## Step 3: Gap Detection

- Validar consistencia entre:
  - flows
  - invariants
  - reglas de negocio

IF inconsistencia:
    STOP
    solicitar aclaración

---

## Step 4: Task Loop

FOR cada tarea en tasks.md:

    ACTUALIZAR /execution/current-task.md antes de delegar (incluir ID y descripción con estado `pending`).

    --- Implementación ---

    CALL backend-agent

    --- Documentación ---

    Validar que todas las funciones/servicios nuevos tengan docstrings y comentarios en español según `specs/engineering/coding-standards.md`.

    --- Testing ---

    CALL testing-agent

    --- Validación ---

    RUN tests

    IF tests FAIL:
        volver a backend-agent

END FOR

---

## Step 5: Review Checkpoint

CALL review-agent

IF rechazo:
    volver a Task Loop

---

## Step 6: Finalization

- Aplicar migraciones
- Actualizar documentación:
  - specs afectados
  - decisions-log.md

- Actualizar:
  - status.md del hito

- Actualizar /execution/current-task.md reportando completion y limpiar si se cierra la tarea.
- Actualizar /execution/current-milestone.md si el hito cambia de fase o se cierra (marcar estado completado, fase siguiente o dejar en blanco). 
- Registrar en /execution/system-state.md cualquier entidad/servicio nueva o cambio de infraestructura que se haya introducido en el hito.

- Generar commit

---

## Step 7: Close Milestone

- Marcar hito como completado
- Limpiar:
  - current-task.md

---

## Error Handling

### Caso: fallo de tests

Loop:
backend-agent → testing-agent → tests

---

### Caso: ambigüedad

STOP inmediato  
Solicitar input del usuario

---

### Caso: rechazo en review

Volver a ejecución  
No avanzar a commit

---

## Guarantees

Este flujo asegura:

- Trazabilidad completa
- No desviación del dominio
- Validación antes de persistencia
