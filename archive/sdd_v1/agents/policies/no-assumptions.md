# No Assumptions Policy

## Principle

Los agentes no deben introducir lógica no definida explícitamente en specs.

---

## Allowed Inference

Se permite inferencia SOLO si:

- es trivial
- no afecta reglas de negocio
- no introduce ambigüedad

Ejemplo permitido:

- naming consistente
- estructura de código

Ejemplo prohibido:

- lógica de pagos
- estados
- reglas de negocio

---

## Missing Information

Si falta información relevante:

- detener ejecución
- generar pregunta al usuario

---

## Question Strategy

Se permite:

- preguntas abiertas (para contexto)
- preguntas cerradas (para decisiones)

---

## Stop Condition

Se debe detener ejecución si:

- hay ambigüedad en reglas
- hay conflicto entre specs
- hay impacto en dominio

---

## Success Criteria

- cero lógica inventada
- toda decisión trazable a specs