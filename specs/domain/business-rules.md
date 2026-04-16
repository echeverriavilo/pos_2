# Reglas de Negocio

## Multitenancy

- Toda operación debe estar asociada a un tenant
- Ninguna query puede ejecutarse sin tenant_id

---

## Flujo con Mesa

- La creación de una mesa ocupada implica la creación de un Order
- Los productos se envían a preparación inmediatamente al ser agregados

---

## Flujo Rápido

- Los productos no se envían a preparación hasta que el pedido esté completamente pagado
- El cambio a estado CONFIRMADO ocurre solo después del pago total

---

## Estados de Order

### Estados válidos

- ABIERTO
- CONFIRMADO
- PAGADO_PARCIAL
- COMPLETADO
- ANULADO

---

## Transiciones válidas

### Flujo con mesa

- ABIERTO → PAGADO_PARCIAL
- ABIERTO → COMPLETADO (si pago total directo)
- PAGADO_PARCIAL → COMPLETADO

---

### Flujo rápido

- ABIERTO → PAGADO_PARCIAL
- PAGADO_PARCIAL → CONFIRMADO (solo cuando total pagado)
- CONFIRMADO → COMPLETADO

---

## Pagos

### Reglas generales

- Un Order puede tener múltiples Transaction
- El total pagado no puede exceder el total del Order

---

### Pago por productos

- Solo puede aplicarse a OrderItem no pagados
- Un OrderItem pagado no puede ser modificado ni anulado

---

### Abonos

- No modifican OrderItem
- Solo afectan el total pendiente

---

## Propina

- Es opcional
- Se almacena en Order.propina_monto solo si el cliente la define

---

## Inventario

### Regla general

El stock se descuenta según el flujo:

#### Flujo con mesa
- Se descuenta inmediatamente al agregar el producto

#### Flujo rápido
- Se descuenta al confirmar el pedido (después del pago total)

---

## Anulación

- No se pueden anular productos ya pagados
- La anulación debe generar reversa de stock si corresponde

--- 

## Acceso de plataforma
- Usuarios con is_platform_staff pueden operar sobre cualquier tenant
- No están restringidos por tenant_id
- Deben ser controlados explícitamente en servicios

---

## Dispositivos y Configuración de Salida

### Generación de Comandos
- En flujo MESA: Se generan comandas al agregar cada producto a la orden (cuando OrderItem entra a PREPARACION)
- En flujo RÁPIDO: Se generan comandas al confirmar el pedido (cuando Order → CONFIRMADO y items entran a PREPARACION)

### Asignación a Dispositivos
- Cada OrderItem se asigna a dispositivos según:
  1. Configuración específica del producto (si existe)
  2. Configuración de la categoría del producto (si existe y no hay config de producto)
  3. Si no hay configuración, se asigna a dispositivo predeterminado del tenant (se define en specs)

### Manejo de Múltiples Dispositivos
- Un mismo OrderItem puede generar múltiples comandas (una por dispositivo configurado)
- Las comandas son independientes (estado, impresión, etc.)