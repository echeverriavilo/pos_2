# Invariantes del Sistema

## Multitenancy

- Toda entidad pertenece a un tenant
- Ninguna operación sin tenant_id

---

## Consistencia de Pagos

- Un Order no puede estar COMPLETADO si el total pagado es menor al total bruto
- Un OrderItem PAGADO no puede cambiar de estado

---

## Consistencia de Inventario

- stock_actual solo puede cambiar mediante StockMovement

---

## Consistencia de Order

- En flujo rápido:
  - no puede existir CONFIRMADO sin pago total

---

## Consistencia de Flujo Mesa

- Una mesa en estado DISPONIBLE no puede tener un Order activo
- Una mesa OCUPADA o PAGANDO debe tener un Order activo