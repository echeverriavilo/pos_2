# Modelo de Datos

## Tenant

- id: UUID
- slug: string (unique)
- nombre: string
- config_iva: decimal (default 0.19)
- config_flujo_mesas: boolean
- created_at: datetime

---

## User

- id: UUID
- email: string (unique)
- first_name: string
- last_name: string
- is_active: boolean
- is_staff: boolean
- is_superuser: boolean
- is_platform_staff: boolean
- pin_hash: string (nullable, almacenado como hash)
- pin_enabled: boolean
- date_joined: datetime

### Reglas

- Usuarios normales tienen tenant vía Membership
- Usuarios platform_staff no tienen tenant (bypass de multitenancy)
- PIN es opcional y de uso operativo (fast login)
- No tiene FK directo a tenant/role - se accede vía property membership

---

## Membership

- user: FK(User)
- tenant: FK(Tenant)
- role: FK(Role)

### Reglas

- Relación 1:1 user ↔ tenant
- Define el rol operativo del usuario en ese tenant

---

## Role

- tenant: FK(Tenant)
- name: string
- description: text
- permissions: M2M(Permission, through RolePermission)
- created_at: datetime

### Reglas

- Nombre único por tenant
- Base roles: administrador, cajero, garzón

---

## Permission

- codename: string (unique)
- description: text

### Permisos del sistema

- create_order
- add_item
- remove_item
- register_payment
- manage_inventory
- manage_users
- manage_tables

---

## RolePermission (through model)

- role: FK(Role)
- permission: FK(Permission)
- active: boolean (default True)
- updated_at: datetime

### Reglas

- Permite toggle activo/inactivo de permisos granulares
- Un rol puede tener el mismo permiso inactive sin haberlo quitado

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
- table: FK(DiningTable, nullable)
- estado: enum (ABIERTO, CONFIRMADO, PAGADO_PARCIAL, COMPLETADO, ANULADO)
- total_bruto: decimal
- propina_monto: decimal

---

## OrderItem

- order: FK(Order)
- product: FK(Product)
- cantidad: int
- precio_unitario_snapshot: decimal
- estado: enum (PENDIENTE, PREPARACION, ENTREGADO, ANULADO, PAGADO)

### Reglas

- tenant forzado desde order
- precio inmutable una vez creado
- Se vuelve inmutable cuando estado = PAGADO

---

## Transaction

- tenant: FK
- order: FK(Order)
- monto: decimal
- tipo_pago: enum (TOTAL, ABONO, PRODUCTOS)

---

## TransactionItem

- transaction: FK(Transaction)
- order_item: FK(OrderItem)
- tenant: FK

### Reglas

- Trazabilidad de qué items fueron pagados en cada transacción