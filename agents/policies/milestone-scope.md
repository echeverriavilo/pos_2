# Milestone Scope Policy

## Principle

Cada hito define un límite estricto de acción.

---

## Scope Rules

El agente:

- solo puede modificar lo necesario para cumplir el hito
- no puede expandir funcionalidad fuera del alcance

---

## Cross-Scope Detection

Si se detecta que:

“otro módulo debería cambiar”

Se debe:

- documentar en decisions-log.md
- NO ejecutar

---

## Exception: Critical Changes

Se permite actuar fuera del scope SOLO si:

- bloquea completamente el hito
- no hay alternativa

Debe:

- justificarse en decisions-log.md

---

## Refactors

Permitidos solo si:

- mejoran el diseño
- están dentro del scope del hito
- no introducen cambios funcionales no requeridos

---

## Prohibitions

- implementación de features futuras
- cambios especulativos

---

## Success Criteria

- el hito se implementa sin contaminar otras áreas