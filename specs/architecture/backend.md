# Backend Architecture

## Stack

- Framework: Django >= 5.0
- ORM: Django ORM
- Base de Datos: PostgreSQL
- Testing: pytest + pytest-django

---

## Project Structure

Arquitectura modular basada en apps Django, con separación estricta de dominio.

Cada app debe seguir la estructura:

- models/
- services/
- selectors/ (lectura de datos)
- tests/

No se permite lógica de negocio en:

- views
- models (más allá de validaciones simples)

---

## Domain Layer

La lógica de negocio debe implementarse en:

- services/

Reglas:

- Cada operación relevante debe ser explícita (no implícita en ORM)
- No se permite lógica distribuida sin control

---

## Transaction Management

- Uso obligatorio de transacciones en operaciones críticas
- Implementación basada en `transaction.atomic`

Casos obligatorios:

- creación de órdenes
- pagos
- cambios de estado
- operaciones de inventario

---

## State Management

Los estados (orders, mesas, pagos) deben:

- definirse explícitamente
- validarse en cada transición
- no permitir estados inválidos

---

## Data Integrity

Se debe garantizar:

- consistencia entre pagos y órdenes
- consistencia de stock
- cumplimiento de invariants definidos en specs

---

## Testing Strategy

- pytest como runner principal
- uso de pytest-django
- tests obligatorios para:
  - servicios
  - reglas de negocio
  - transiciones de estado

---

## Constraints

- No uso de lógica implícita del ORM para reglas críticas
- No signals para lógica de negocio
- No side-effects ocultos

---

## Success Criteria

El backend es válido si:

- toda lógica está en services
- todas las operaciones críticas son transaccionales
- no existen inconsistencias de estado