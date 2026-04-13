# Acceptance Criteria — Hito 3: DiningTable

## Objetivo

Implementar la entidad DiningTable y su gestión de estados, asegurando consistencia con el flujo con mesas y las invariantes del sistema.

---

## Criterios de Aceptación

### Creación

- Se puede crear una DiningTable con:
  - tenant
  - numero
  - estado inicial = DISPONIBLE

---

### Estados válidos

- DISPONIBLE
- OCUPADA
- PAGANDO
- RESERVADA

---

### Consistencia con Orders

- Una mesa en estado DISPONIBLE:
  - NO puede tener Order activo

- Una mesa en estado OCUPADA o PAGANDO:
  - DEBE tener exactamente un Order activo

---

### Apertura de mesa

- Al abrir una mesa:
  - estado → OCUPADA
  - se crea un Order:
    - tipo_flujo = MESA
    - estado = ABIERTO
    - asociado a la mesa

---

### Cambio a PAGANDO

- Se puede cambiar una mesa de OCUPADA → PAGANDO

- Desde PAGANDO:
  - se puede volver a OCUPADA si se agregan productos

---

### Cierre de mesa

- Cuando el Order asociado:
  - estado → COMPLETADO

Entonces:

- mesa → DISPONIBLE

---

### Restricciones

- No se puede abrir una mesa que:
  - no esté en estado DISPONIBLE

- No se puede tener más de un Order activo por mesa

---

### Multitenancy

- Todas las operaciones deben:
  - estar filtradas por tenant
  - validar consistencia de tenant entre mesa y order

---

### Validación de invariantes

Debe cumplirse:

- "Una mesa DISPONIBLE no puede tener un Order activo"
- "Una mesa OCUPADA o PAGANDO debe tener un Order activo"