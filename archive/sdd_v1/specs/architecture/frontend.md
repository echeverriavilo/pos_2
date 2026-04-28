# Frontend Architecture

## Stack

- HTML server-rendered (Django Templates)
- HTMX (uso básico)
- Bootstrap (instalación local)

---

## UI Model

- Interfaz basada en renderizado desde backend
- HTMX utilizado para:
  - actualizaciones parciales
  - interacción sin recarga completa

---

## HTMX Usage

Uso permitido:

- hx-get
- hx-post
- hx-target
- hx-swap

Restricciones:

- No lógica compleja en cliente
- No manejo de estado fuera del backend

---

## Bootstrap

- Instalación local (no CDN)
- Uso para:
  - layout
  - componentes básicos

---

## State Representation

La UI debe reflejar estados reales del dominio:

Ejemplos:

- mesa disponible
- mesa ocupada
- mesa pagando
- pedido en preparación
- pedido completado

No se permite:

- estados inventados en frontend

---

## Interaction Rules

Toda acción del usuario:

→ debe mapear a una operación backend

Ejemplo:

- abrir mesa → endpoint backend
- pagar → endpoint backend

---

## Constraints

- No SPA
- No frameworks JS adicionales
- No lógica de negocio en frontend

---

## Evolution

- HTMX se usa en modo básico inicialmente
- patrones avanzados se introducen en etapas posteriores

---

## Success Criteria

El frontend es válido si:

- refleja correctamente los estados del sistema
- no contiene lógica de negocio
- todas las acciones dependen del backend