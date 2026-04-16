# Testing Strategy

## Core Principle

Los tests validan:

- reglas de negocio
- invariantes
- flujos del sistema

No solo validan código.

---

## Stack

- pytest
- pytest-django

---

## Test Types

### 1. Unit Tests

Validan:

- servicios
- lógica de negocio

Ejemplo:

- creación de orden
- aplicación de pago parcial
- cambio de estado

---

### 2. Integration Tests

Validan:

- interacción entre componentes
- persistencia en base de datos

Ejemplo:

- flujo completo de pedido
- flujo de pago

---

## Test Scope Rules

Cada regla de negocio debe tener al menos un test.

Cada flujo definido en `flows.md` debe estar cubierto.

---

## Critical Scenarios (obligatorios)

### Órdenes con mesa

- apertura de mesa
- múltiples pedidos
- cambio a estado pagando
- reversión a ocupado
- cierre de mesa

---

### Órdenes sin mesa

- creación de pedido
- pago completo
- paso a preparación
- entrega

---

### Pagos

- pago total
- pago parcial por productos
- pago parcial por monto
- múltiples pagos

---

### Propina
- cálculo sugerido (10%)
- aceptación
- rechazo
- monto personalizado

---

### Dispositivos
- generación correcta de comandas por dispositivo según configuración
- manejo de múltiples dispositivos para un mismo producto
- asignación de producto a dispositivo específico
- asignación de categoría a dispositivo
- resolución de conflictos por prioridad
- dispositivo predeterminado cuando no hay configuración específica

---

### Stock

- descuento en flujo con mesa
- descuento en flujo sin mesa (post pago)

---

## Naming Convention

Formato:

test_<acción>_<condición>_<resultado>

Ejemplo:

- test_apply_partial_payment_reduces_balance
- test_order_moves_to_preparing_when_paid

---

## Isolation Rules

- tests deben ser independientes
- no depender de estado previo

---

## Database Usage

- uso de base de datos de test (pytest-django)
- rollback automático entre tests

---

## Assertions

Deben validar:

- estado final
- efectos secundarios
- integridad de datos

---

## Failure Policy

Si un test falla:

→ el hito NO puede avanzar

---

## Coverage Requirement

- cobertura funcional completa
- no se mide % de líneas, sino cobertura de reglas

---

## Success Criteria

Los tests son válidos si:

- reflejan reglas reales del negocio
- detectan errores de lógica
- garantizan consistencia del sistema