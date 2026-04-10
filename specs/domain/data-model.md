# Modelo de Datos

## Tenant

- id: UUID
- nombre: string
- config_iva: decimal (default 0.19)
- config_flujo_mesas: boolean
- created_at: datetime

---

## User

- email
- password
- tenant: FK(Tenant, null=True)
- role: FK(Role, null=True)
- is_superuser: Boolean
- is_platform_staff: Boolean
- pin: CharField (nullable, almacenado como hash)

### Reglas

- Usuarios normales deben tener tenant
- Usuarios platform_staff no tienen tenant
- role solo aplica a usuarios con tenant
- PIN es opcional y de uso operativo

---

## Category

- tenant: FK
- nombre: string

---

## Product

- tenant: FK
- category: FK
- nombre: string
- precio_bruto: decimal
- es_inventariable: boolean
- stock_actual: decimal

---

## StockMovement

- tenant: FK
- product: FK
- tipo: enum (INGRESO, AJUSTE, VENTA)
- cantidad: decimal

---

## DiningTable

- tenant: FK
- numero: string
- estado: enum (DISPONIBLE, OCUPADA, PAGANDO, RESERVADA)

---

## Order

- tenant: FK
- tipo_flujo: enum (MESA, RAPIDO)
- table: FK nullable
- estado: enum (ABIERTO, CONFIRMADO, PAGADO_PARCIAL, COMPLETADO, ANULADO)
- total_bruto: decimal
- propina_monto: decimal

---

## OrderItem

- order: FK
- product: FK
- cantidad: int
- precio_unitario_snapshot: decimal
- estado: enum (PENDIENTE, PREPARACION, ENTREGADO, ANULADO, PAGADO)

---

## Transaction

- tenant: FK
- order: FK
- monto: decimal
- tipo_pago: enum (TOTAL, ABONO, PRODUCTOS)

---

## TransactionItem

- transaction: FK
- order_item: FK