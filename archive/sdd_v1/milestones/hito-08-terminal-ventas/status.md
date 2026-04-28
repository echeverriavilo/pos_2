# Hito 08 - Status

## Estado

Completado

---

## Progreso

- Tareas: 6/6
- Tests: 5/5 (terminal de ventas)
- Total tests: 65/65 pasando

---

## Funcionalidades implementadas

1. Grid de productos con categorías
2. Buscador reactivo (HTMX con delay de 500ms)
3. Carrito de compras reactivo
4. Agregar productos al carrito
5. Quitar productos del carrito
6. Cálculo automático de totales

---

## Bugs corregidos

- HTMX no estaba cargado (agregado CDN)
- CSRF token no se enviaba en peticiones HTMX
- Nombres de campos en español vs inglés (nombre, precio_bruto)
- Permissions actualizados: `add_item`, `remove_item`
- Tests actualizados para usar nuevos nombres de permissions
