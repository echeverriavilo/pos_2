# Definition — Hito 4: Órdenes

## Entidades

### Order

- tenant: FK(Tenant)
- tipo_flujo: enum (MESA, RAPIDO)
- table: FK(DiningTable, nullable)
- estado: enum
- total_bruto: decimal
- propina_monto: decimal

---

### OrderItem

- order: FK(Order)
- product: FK(Product)
- cantidad: int
- precio_unitario_snapshot: decimal
- estado: enum

---

## Estados Order

- ABIERTO
- CONFIRMADO
- PAGADO_PARCIAL
- COMPLETADO
- ANULADO

---

## Estados OrderItem

- PENDIENTE
- PREPARACION
- ENTREGADO
- ANULADO
- PAGADO

---

## Operaciones de Dominio

### create_order

- inicializa Order en estado ABIERTO

---

### add_item

- crea OrderItem
- recalcula total_bruto
- aplica lógica de estado según flujo

---

### remove_item

- solo permitido si:
  - estado != PAGADO

- debe marcar como ANULADO

---

### recalculate_total

- recalcula total_bruto basado en items no anulados

---

### transition_order_state

- valida transiciones según flujo

---

## Reglas de Negocio

- precio_unitario_snapshot es inmutable
- total_bruto es derivado (no editable manualmente)

---

## Dependencias

- Product
- DiningTable
- (Pagos se integran en siguiente hito)