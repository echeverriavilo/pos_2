# Hito 11 - Status

## Estado

Completado

---

## Progreso

- Tareas: 9/9
- Tests: 100/100 pasando (15 payment_calculator + 7 hito11_corrections + 78 existentes)

---

## Implementado

### Backend Services
- `PaymentCalculator`: `calculate_iva_breakdown`, `calculate_suggested_tip`, `set_tip`
- `TransactionSelector`: `total_cuenta`, `total_pending` (actualizado), `items_paid_amount`
- `OrderItemSelector`: `get_unpaid_items`, `get_paid_items`
- `update_order_payment_state`: actualizado para usar `total_cuenta` en lugar de `total_bruto`

### Views (6 nuevas)
- `mesa_solicitar_cuenta`: OCUPADA → PAGANDO
- `mesa_modal_pago`: modal de pago con desglose completo
- `orden_fijar_propina`: fija propina y retorna modal actualizado
- `orden_procesar_pago`: procesa pago (TOTAL/ABONO/PRODUCTOS)
- `orden_pre_cuenta`: pre-cuenta detallada
- `terminal_modal_pago`: modal de pago para flujo rápido

### Templates (11)
- `modal_pago.html`: modal con desglose, tabs de pago, selector de items
- `desglose_cuenta.html`: componente de desglose
- `propina_selector.html`: selector de propina con edición inline (botones %/$ personalizado)
- `selector_items_pago.html`: checkboxes para pago por productos (fetch() API)
- `formulario_abono.html`: input de monto para abono (fetch() API)
- `pre_cuenta.html`: ticket con items pagados/no pagados
- `pago_exitoso.html`: confirmación de pago
- `terminal_modal_pago.html`: modal para flujo rápido
- `cuenta_actualizada.html`: 3 tarjetas (Productos, Desglose, Total) con badges de pagado
- `mesa_pedido.html`: 3 tarjetas separadas (Productos, Desglose, Total), sticky bar inferior
- `mesa_actions.html`: acciones condicionales según `has_active_items`

### URLs (6 nuevas)
- `mesa/<table_id>/solicitar-cuenta/`
- `mesa/<table_id>/modal-pago/`
- `orden/<order_id>/fijar-propina/`
- `orden/<order_id>/procesar-pago/`
- `orden/<order_id>/pre-cuenta/`
- `terminal-ventas/modal-pago/`

---

## Decisión de diseño

- **total_cuenta = total_bruto + propina_monto**: La propina se incluye en el total a pagar
- **Condición de completado**: `total_paid >= total_cuenta` (no `total_bruto`)
- **Propina opcional**: Puede ser 0, personalizada o 10% sugerido
- **Pago por productos**: Solo disponible en flujo MESA, bloqueado después de ABONO
- **fetch() sobre HTMX para POST**: Todos los formularios de pago usan `fetch()` con CSRF de `<meta>` tag
- **Selección de template por `order.table_id`**: `modal_pago.html` vs `terminal_modal_pago.html`
- **Propina 10% por defecto**: Se auto-aplica al abrir modal de pago si `propina_monto == 0`
- **Sticky bar**: Barra de acciones usa `position: sticky; bottom: 0` dentro de `.content-area`

---

## Tests

- `test_payment_calculator.py`: 15 tests nuevos
- `test_hito11_corrections.py`: 7 tests de corrección
- `test_payments.py`: 14 tests existentes (sin regresiones)
- `test_services.py`: 7 tests existentes (sin regresiones)
- Total suite: 100 tests pasando

---

## Issues corregidos post-review (ronda 1)

1. **propina_selector destruía modal**: `orden_fijar_propina` ahora retorna modal completo
2. **selector_items_pago no funcionaba con HTMX**: Script usa `htmx:afterSwap` + `DOMContentLoaded`
3. **cuenta_actualizada mostraba precio unitario**: Cambiado a `item.get_total`

---

## Issues corregidos post-review (ronda 2)

### Bug fixes en views.py
1. **`mesa_liberar_mesa`**: Cambiado `set_table_paying()` por `release_table()` para cerrar mesas sin movimientos correctamente
2. **`orden_procesar_pago`**: Agregada variable `table` a los 3 contextos de `render()` (faltaba, causaba NoReverseMatch en flujo de mesa)
3. **`orden_procesar_pago`**: Condición de completado cambiada de solo `Order.States.COMPLETADO` a `Order.States.COMPLETADO or Order.States.CONFIRMADO` (flujo rápido transiciona a CONFIRMADO, no COMPLETADO)
4. **`mesa_modal_pago` y `terminal_modal_pago`**: Auto-aplicar propina 10% cuando `order.propina_monto == 0`

### Bug fixes en templates
5. **Todos los modales de pago reescritos**: Reemplazado `hx-post` con `fetch()` para confiabilidad CSRF. Funciones: `getCsrfToken()`, `paymentFetch()`, `submitTotalPayment()`, `submitAbono()`, `submitProductsPayment()`, `applyTip()`, `applyCustomPct()`, `applyCustomFixed()`, `toggleTipCustomPct()`, `toggleTipCustomFixed()`, `cancelTipEdit()`
6. **`propina_selector.html`**: Eliminado modal Bootstrap anidado, reemplazado con edición inline con botones personalizados %/$
7. **`selector_items_pago.html`**: Eliminado `htmx:configRequest` roto, usa `fetch()` con `FormData`
8. **`formulario_abono.html`**: Reemplazado `hx-post` con `onclick="submitAbono()"`
9. **`mesa_pedido.html`**: Reestructurado en 3 tarjetas separadas (Productos, Desglose, Total), sticky bar inferior para botones de acción (sin solapar sidebar)
10. **`cuenta_actualizada.html`**: Misma estructura de 3 tarjetas con desglose completo (Neto, IVA, Subtotal, Propina, Total, Pagado, Pendiente)
11. **`mesa_actions.html`**: Eliminado botón "Ver Cuenta" (info ahora inline), renderizado condicional según `has_active_items`

### Bug fix en redirect
12. **`mesa_liberar_mesa` redirect**: Cambiado de `/ordenes/mesa/{id}/` a `/salon/mesas/`