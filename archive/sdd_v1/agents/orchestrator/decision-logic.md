# Orchestrator Decision Logic

## Core Principle

El orquestador opera bajo un modelo:

→ 1 hito = 1 sesión completa de ejecución

No existe ejecución parcial fuera de este marco.

---

## Execution Mode

- Modo principal: secuencial
- Paralelismo: permitido solo cuando no hay dependencia directa

Ejemplo válido:
- Generación de tests DESPUÉS de que una unidad de código está estable

Ejemplo inválido:
- Testing antes de implementación backend

---

## Milestone Lock

Durante una sesión:

- Solo se permite trabajar sobre:
  /milestones/<hito_actual>/*

- Está prohibido:
  - modificar otros hitos
  - anticipar features futuras
  - redefinir arquitectura fuera del scope

---

## Phase Model

Cada sesión se divide en fases estrictas:

### 1. Analysis Phase

Objetivo:

- Entender estado actual del sistema
- Entender alcance del hito

Acciones:

- Leer specs relevantes
- Leer estado del proyecto
- Leer milestone actual

---

### 2. Scope Definition

Objetivo:

- Delimitar exactamente qué se puede tocar

Acciones:

- Identificar entidades afectadas
- Identificar reglas involucradas
- Identificar límites del sistema

Restricción:

- No expandir scope bajo ninguna circunstancia

---

### 3. Gap Detection

Objetivo:

- Detectar vacíos de diseño

Acciones:

- Validar consistencia entre:
  - flows.md
  - business-rules.md
  - invariants.md

Si hay inconsistencia:

→ DETENER ejecución  
→ Generar preguntas al usuario

Regla crítica:

- Nunca asumir información faltante

---

### 4. Execution Phase

Objetivo:

- Implementar el hito completamente

Subfases:

#### 4.1 Backend Implementation
- Delegar a backend-agent

#### 4.2 Documentation in Code
- Toda función debe estar comentada

#### 4.3 Testing
- Delegar a testing-agent

#### 4.4 Validation
- Ejecutar tests

Condición:

- Si falla un test → volver a implementación

Loop permitido:

implementation ↔ testing

---

### 5. Checkpoint Review

Objetivo:

- Validación final antes de cerrar hito

Acción:

- Delegar a review-agent

El review valida:

- cumplimiento de acceptance.md
- alineación con specs
- ausencia de desviaciones

---

### 6. Finalization Phase

Solo si todo es válido:

Acciones:

- Aplicar migraciones
- Actualizar documentación
- Registrar decisiones en:
  /execution/decisions-log.md

- Generar commit lógico

---

## Parallelism Rules

El orquestador puede paralelizar SOLO si:

- Las tareas no comparten dependencias
- No comprometen consistencia del dominio

Ejemplos permitidos:

- Tests de módulos ya estables
- Documentación no crítica

Ejemplos prohibidos:

- Lógica de negocio + tests simultáneos sobre código inestable

---

## Stop Conditions

El sistema debe detenerse si:

- Falta una regla de negocio clave
- Hay conflicto entre specs
- Hay ambigüedad en estados o flujos

---

## Success Criteria

Un hito se considera completado si:

- Todos los tests pasan
- Review-agent aprueba
- Documentación está actualizada
- No hay violaciones de specs