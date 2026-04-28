# Hito 10 - Status

## Estado

Completado (backend de comandas con dispositivos y configuración de salida)

---

## Progreso

- Tareas: 8/8 (backend)
- Tests: 8/8 (comanda) + 78 total suite

---

## Implementado

### Modelos
- `Dispositivo`: dispositivo de salida (IMPRESORA/PANTALLA) tenant-aware, campo activo, nombre único por tenant
- `ConfiguracionDispositivo`: asignación producto/categoría → dispositivo con prioridad, validación XOR producto↔categoría
- `Comanda`: orden de preparación para un dispositivo específico, estados PENDIENTE/LISTA/ENTREGADO/CANCELADO
- `ComandaItem`: relación comanda↔order_item con snapshot de cantidad y precio

### Servicios
- `DispositivoService`: create, update, delete (lógico), get_activos, get_default_for_tenant
- `ComandaService`: generar_comandas_para_order_item, actualizar_estado_comanda con validación de transiciones

### Selectores
- `DispositivoSelector`: consultas por tenant y nombre
- `ConfiguracionDispositivoSelector`: resolución de configuración efectiva (producto > categoría > predeterminado)
- `ComandaSelector`: pendientes por dispositivo, por orden, con items prefetch

### Integración con flujos existentes
- Flujo MESA: comandas se generan automáticamente al agregar items (estado PREPARACION)
- Flujo RÁPIDO: comandas se generan al confirmar pedido (después de pago total)
- `transition_order_state` ahora acepta parámetro `user` para pasar a servicios de comanda
- `update_order_payment_state` ahora acepta parámetro `user` y lo propaga

### Constantes
- `SystemActions.MANAGE_DEVICES`: nuevo permiso para gestión de dispositivos

### Migraciones
- 0004: Dispositivo, Comanda, ComandaItem, ConfiguracionDispositivo

---

## Deciciones clave

1. Entidad Comanda separada de OrderItem: permite agrupar items por dispositivo y rastrear estado de preparación independientemente del estado de pago del item
2. Dispositivo predeterminado: si no hay configuración específica, se usa el primer dispositivo activo ordenado por nombre
3. ConfiguracionDispositivo con XOR: una configuración apunta a producto O categoría, nunca ambos, nunca ninguno
4. Prioridad en configuración: config de producto tiene prioridad sobre config de categoría por ordenamiento descendente de prioridad
5. Dispositivos inactivos excluidos: la resolución de configuración filtra dispositivos inactivos, no se generan comandas para ellos

---

## Pendiente para UI

La interfaz visual de cocina/barra (tarjetas, polling HTMX, botones de estado) no se implementó en este ciclo. El backend está listo para soportarla.

---

## Tests

- test_create_dispositivo ✓
- test_update_dispositivo ✓
- test_configuracion_producto_tiene_prioridad_sobre_categoria ✓
- test_flujo_mesa_genera_comanda_al_agregar_item ✓
- test_flujo_rapido_genera_comandas_al_confirmar ✓
- test_dispositivo_inactivo_no_recibe_comandas ✓
- test_transiciones_estado_comanda_validas ✓
- test_transiciones_estado_comanda_invalidas_lanzan_error ✓