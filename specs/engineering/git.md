# Git Strategy

## Core Principle

El control de versiones debe reflejar:

- hitos completos
- cambios coherentes
- trazabilidad con el dominio

---

## Branching Strategy

- Uso exclusivo de rama main
- No se utilizan ramas adicionales en esta etapa (MVP)

---

## Commit Model

- 1 commit por hito completado
- No se permiten commits intermedios

---

## Commit Timing

El commit se realiza únicamente cuando:

- todos los tests pasan
- el review-agent aprueba
- la documentación está actualizada
- el hito está completamente implementado

---

## Commit Content

Cada commit debe incluir:

- código implementado
- tests asociados
- migraciones (si aplica)
- actualizaciones en specs (si hubo decisiones)

---

## Commit Message

Formato:

- idioma: español
- descriptivo
- enfocado en resultado funcional

Ejemplos:

- "Implementa flujo completo de órdenes con mesa"
- "Agrega soporte para pagos parciales por monto"
- "Implementa lógica de descuento de stock por flujo"

---

## Prohibiciones

No se permite:

- commits parciales
- commits sin tests
- commits sin coherencia funcional
- mensajes ambiguos ("fix", "update", etc.)

---

## Traceability

Cada commit debe permitir identificar:

- funcionalidad implementada
- reglas de negocio afectadas
- hito correspondiente

---

## Constraints

- el repositorio siempre debe estar en estado consistente
- no se permite código incompleto en main

---

## Success Criteria

La estrategia es correcta si:

- cada commit representa un hito completo
- el historial refleja evolución del sistema
- no existen estados inconsistentes en el repositorio