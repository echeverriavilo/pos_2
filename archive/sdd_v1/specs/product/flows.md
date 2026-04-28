# Flujos de Operación

## Tipos de Flujo

El sistema soporta dos tipos de flujo configurables por tenant:

- Flujo con mesas
- Flujo rápido (sin mesas)

---

## Flujo con Mesa

### Apertura de Mesa

1. Cliente llega a mesa DISPONIBLE
2. Garzón abre la mesa
3. Estado de mesa → OCUPADA
4. Se crea Order en estado ABIERTO

---

### Consumo

- El cliente puede pedir múltiples veces
- Cada pedido:
  - puede contener uno o más productos
  - genera una comanda
- Los productos se envían a preparación inmediatamente al ser agregados [MESA] o al confirmar el pedido [RÁPIDO], generando las comandas correspondientes para cada dispositivo configurado.

---

### Estado Pagando

1. Cliente solicita la cuenta
2. Mesa cambia a estado PAGANDO

Desde este estado:

- Puede volver a OCUPADA si se agregan productos
- Puede avanzar a pago

---

### Pago
- Puede ser:
  - total
  - parcial (ver sección pagos)

### Generación de Comandos
- Flujo MESA: Al agregar productos a la orden (cada adición genera comandas para dispositivos configurados)
- Flujo RÁPIDO: Al transicionar a estado CONFIRMADO (genera comandas para todos items pendientes)

---

### Cierre

- Cuando el total de la orden está pagado:
  - Order → COMPLETADO
  - Mesa → DISPONIBLE

---

## Flujo Rápido

### Creación

1. Se crea Order en estado ABIERTO
2. Se agregan productos

---

### Pago

- El pedido debe pagarse (total o parcial)

---

### Confirmación

- Una vez pagado completamente:
  - Order → CONFIRMADO
  - Se envía a preparación

---

### Entrega

- Cocina/barra entrega productos
- Order → COMPLETADO

---

## Pagos Parciales

### Tipos de Pago

#### 1. Por Productos

- Se seleccionan OrderItem específicos
- Esos ítems pasan a estado PAGADO

Efecto:

- Al reemitir cuenta:
  - no deben aparecer los productos pagados

---

#### 2. Por Monto (Abono)

- Se ingresa un monto arbitrario

Efecto:

- No modifica los ítems
- Se descuenta del total general

---

## Propina

- Es opcional
- Es configurable por tenant
- Sugerencia: 10% del total

El cliente puede:

- no dejar propina
- dejar un monto distinto
- dejar un porcentaje distinto