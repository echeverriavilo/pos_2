# Hito 10 - Tasks

## Tareas Backend (Completadas)

1. [x] Crear modelo Dispositivo (IMPRESORA/PANTALLA, tenant-aware, activo)
2. [x] Crear modelo ConfiguracionDispositivo (producto XOR categoría, prioridad)
3. [x] Crear modelo Comanda y ComandaItem (estados PENDIENTE/LISTA/ENTREGADO/CANCELADO)
4. [x] Crear DispositivoService (CRUD + get_default_for_tenant)
5. [x] Crear ComandaService (generación automática, transiciones de estado)
6. [x] Crear selectores (DispositivoSelector, ConfiguracionDispositivoSelector, ComandaSelector)
7. [x] Integrar generación de comandas en add_or_update_item_in_order (flujo MESA)
8. [x] Integrar generación de comandas en transition_order_state CONFIRMADO (flujo RÁPIDO)
9. [x] Agregar permiso manage_devices a SystemActions
10. [x] Tests del módulo de comandas (8 tests)

## Tareas Frontend (Pendientes)

1. [ ] View de comandas (cocina/barra)
2. [ ] Tarjetas de pedidos por dispositivo
3. [ ] Listado de items por pedido
4. [ ] Polling HTMX para actualizaciones
5. [ ] Botones de cambio de estado de comanda
6. [ ] Filtros por tipo de producto/dispositivo
7. [ ] Notificación visual de nuevos pedidos