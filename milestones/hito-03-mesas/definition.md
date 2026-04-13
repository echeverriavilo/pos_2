# Definition — Hito 3: DiningTable

## Entidad

### DiningTable

- tenant: FK(Tenant)
- numero: string
- estado: enum

---

## Estado (enum)

- DISPONIBLE
- OCUPADA
- PAGANDO
- RESERVADA

---

## Relaciones

- DiningTable 1 → 0..1 Order activo

---

## Concepto de Order Activo

Un Order activo es aquel cuyo estado es:

- ABIERTO
- PAGADO_PARCIAL
- CONFIRMADO

No incluye:

- COMPLETADO
- ANULADO

---

## Operaciones de Dominio

### create_table

Crea una mesa en estado DISPONIBLE

---

### open_table

- Precondiciones:
  - estado = DISPONIBLE

- Efectos:
  - estado → OCUPADA
  - crear Order asociado:
    - tipo_flujo = MESA
    - estado = ABIERTO

---

### set_table_paying

- Precondición:
  - estado = OCUPADA

- Efecto:
  - estado → PAGANDO

---

### reopen_table

- Precondición:
  - estado = PAGANDO

- Efecto:
  - estado → OCUPADA

---

### close_table

- Trigger:
  - Order asociado pasa a COMPLETADO

- Efecto:
  - estado → DISPONIBLE

---

## Reglas

- No puede existir más de un Order activo por mesa
- estado debe ser consistente con existencia de Order activo

---

## Dependencias

- Order (solo a nivel de contrato, no implementación completa)