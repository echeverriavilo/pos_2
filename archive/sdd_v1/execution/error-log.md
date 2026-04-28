# Error Log

## Entry Format

- Fecha
- Error
- Síntoma
- Causa
- Solución

---

## Entries

- Fecha: 2026-04-16
  - Error: Elementos con altura equivalente a toda la pantalla
  - Síntoma: Tarjetas de productos, líneas de cuenta y otros elementos mostraban altura de 100vh
  - Causa: Regla CSS genérica `.d-flex { min-height: 100vh; }` en grastro.css que afectaba a TODOS los elementos con clase d-flex de Bootstrap
  - Solución: 
    1. Reemplazar `.d-flex` genérico con `.app-layout` específico
    2. Actualizar base.html para usar `class="app-layout"` en contenedor principal
    3. Redefinir layout con altura fija y overflow interno en lugar de min-height en múltiples niveles
  - Archivos afectados: grastro/templates/grastro/base.html, static/css/grastro.css

- Fecha: 2026-04-16
  - Error: Método incorrecto `get_active_products` en ProductSelector
  - Síntoma: AttributeError al acceder a vista mesa_pedido
  - Causa: Uso de método inexistente `get_active_products` en lugar de `search_active_products`
  - Solución: Corregir llamadas a `ProductSelector.search_active_products()`
  - Archivos afectados: apps/orders/views.py

- Fecha: 2026-04-16
  - Error: Campo `categoria_id` vs `category_id` en template
  - Síntoma: Filtros por categoría no funcionaban
  - Causa: Uso de `categoria_id` en template cuando el modelo usa `category_id`
  - Solución: Actualizar todas las referencias a `product.category_id` en templatemesa_pedido.html y datos JS
  - Archivos afectados: apps/orders/templates/orders/mesa_pedido.html

- Fecha: 2026-04-16
  - Error: Test fallando por producto inexistente
  - Síntoma: Test `test_confirmar_pedido_mesa_pagando_vuelve_ocupada` fallaba con 404 (producto ID 1 inexistente)
  - Causa: Test usaba ID hardcodeado en lugar de crear producto real via fixture
  - Solución: 
    1. Añadir fixture `test_product` en test_ui_tables.py
    2. Actualizar test para usar `test_product.pk`
    3. Añadir fixture a la clase de test
  - Archivos afectados: apps/dining/tests/test_ui_tables.py

- Fecha: 2026-04-16
  - Error: Filtros por categoría no funcionando después de corrección de campo
  - Síntoma: Filtros mostraban/ocultaban productos incorrectamente
  - Causa: Comparación incorrecta en JavaScript (usando null/undefined para "Todos" vs. comparaciones estrictas con category_id)
  - Solución: 
    1. Cambiar valor de "Todos" de `null` a `0` (categoría especial)
    2. Actualizar lógica de filtro para tratar 0 como mostrar todos
    3. Asegurar consistencia entre valor inicial del chip "Todos" y comparación
  - Archivos afectados: apps/orders/templates/orders/mesa_pedido.html (JS filterCategory)

- Fecha: 2026-04-16
  - Error: Función duplicada mesa_nuevo_pedido_modal en views.py
  - Síntoma: Views.py tenía función duplicada causing confusión
  - Causa: Edit anterior dejó código duplicado
  - Solución: Reescribir views.py completamente para eliminar duplicados
  - Archivos afectados: apps/orders/views.py