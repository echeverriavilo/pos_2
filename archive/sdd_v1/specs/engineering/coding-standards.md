# Coding Standards

## Core Principle

El código debe ser:

- explícito
- trazable a specs
- sin ambigüedad
- sin lógica implícita

---

## Language Convention

- Variables y funciones: inglés
- Clases: inglés
- Docstrings y comentarios: español
- Mensajes de commit: español
- Idioma funcional de la app: español

---

## Regional Settings

Configuración obligatoria:

- Timezone: America/Santiago
- Locale: es_CL

Todo manejo de fechas, horas y formatos debe respetar esta configuración.

---

## Project Structure

Cada app debe seguir:

- models/
- services/
- selectors/
- tests/

No se permite:

- lógica de negocio fuera de services/

---

## Naming Conventions

### Clases

- PascalCase
- Ejemplo:
  - Order
  - Payment
  - Table

---

### Funciones

- snake_case
- Deben describir acción explícita

Ejemplo:

- create_order
- apply_partial_payment
- change_order_status

---

### Variables

- snake_case
- nombres descriptivos

Prohibido:

- abreviaciones ambiguas
- nombres genéricos (data, obj, tmp)

---

## Service Layer Rules

Cada servicio debe:

- representar una acción de negocio
- ser explícito
- no tener efectos secundarios ocultos

Ejemplo correcto:

- create_order(...)
- apply_partial_payment(...)

Ejemplo incorrecto:

- process(...)
- handle(...)

---

## Function Structure

Toda función debe:

1. validar inputs
2. ejecutar lógica
3. retornar resultado explícito

---

## Docstrings

Todas las funciones deben tener docstring en español.

Formato mínimo:

- Descripción clara de la función
- Parámetros
- Retorno
- Efectos secundarios (si aplica)

---

## Comments

Se deben usar comentarios cuando:

- hay reglas de negocio
- la lógica no es trivial

No se permite:

- comentarios redundantes

---

## Error Handling

- errores deben ser explícitos
- no se permite manejo silencioso

Prohibido:

- try/except sin manejo claro

---

## Transactions

Operaciones críticas:

- deben ser atómicas
- deben usar transaction.atomic

---

## Imports

- ordenados
- sin imports innecesarios

---

## Tests Alignment

Cada unidad de lógica debe:

- tener test asociado
- ser testeable de forma aislada

---

## Prohibitions

- lógica de negocio en views
- lógica compleja en models
- uso de signals para reglas de negocio
- side-effects ocultos

---

## Readability

El código debe leerse como:

→ una representación directa del dominio

---

## Success Criteria

El código cumple estándar si:

- es consistente
- es explícito
- refleja reglas de negocio sin ambigüedad