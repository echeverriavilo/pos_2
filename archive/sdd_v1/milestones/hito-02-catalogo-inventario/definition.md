# Hito 02 — Catálogo e Inventario

## Objetivo

Implementar:

- catálogo de productos
- sistema básico de inventario
- control de stock

---

## Dominio

### Product

- nombre
- precio
- categoría
- imagen
- es_inventariable (boolean)
- stock_actual (persistido)

---

### Variantes

- Cada variante es un producto independiente
- No existe entidad separada de variantes

---

### Category

- definida por cada tenant
- organiza productos

---

### Ingredient

- entidad base
- sin lógica de recetas en este hito

---

### StockMovement

- registra cambios de stock

Tipos:

- ingreso
- ajuste
- venta (definido pero aún nose implenta en este hito)

---

## Inventario

### Modelo

- StockMovement → histórico
- Product.stock_actual → estado actual

---

### Reglas

- stock se actualiza en cada movimiento
- no se calcula dinámicamente

---

### Venta

- solo productos inventariables validan stock
- productos no inventariables pueden venderse sin restricción

---

## Alcance

Incluye:

- CRUD de productos
- CRUD de categorías
- sistema de inventario
- movimientos de stock

---

## Fuera de alcance

- recetas
- costos
- análisis de inventario
- automatizaciones complejas