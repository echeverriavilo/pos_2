# Hito 10 - Acceptance Criteria

## Funcionalidad Básica
✅ Sistema permite crear y configurar dispositivos de salida (impresoras/pantallas)
✅ Sistema permite configurar qué productos/categorías van a cada dispositivo
✅ Sistema respeta prioridad en configuración de dispositivos
✅ Sistema tiene dispositivo predeterminado por tenant

## Generación de Comandos - Flujo Mesa
✅ Al agregar un producto a una orden abierta (MESA), se generan comandas para todos los dispositivos configurados para ese producto
✅ Si un producto tiene múltiples configuraciones de dispositivo, se genera una comanda por cada dispositivo
✅ Si no hay configuración específica, se usa dispositivo predeterminado del tenant
✅ Las comandas reflejan el estado actual de los OrderItems (cantidad, precio)

## Generación de Comandos - Flujo Rápido
✅ Al confirmar una orden rápida (pago total alcanzado), se generan comandas para todos los OrderItems pendientes
✅ La generación sigue las mismas reglas de asignación a dispositivos que en flujo mesa
✅ No se generan comandas duplicadas para el mismo OrderItem-dispositivo combinación

## Estado y Transiciones
✅ Las comandas tienen estado: PENDIENTE, LISTA, ENTREGADO, CANCELADO
✅ Las transiciones de estado siguen reglas de negocio definidas (PENDIENTE→LISTA→ENTREGADO)
✅ El estado de comanda no afecta el estado de OrderItem o Orden

## Integración y Consistencia
✅ Multitenancy: configuración y comandas están aisladas por tenant
✅ Consistencia: no se pueden generar comandas para ordenes en estados inválidos (ANULADO)
✅ Dispositivo inactivo no recibe comandas
✅ Reversibilidad: si se elimina configuración, las comandas futuras respetan la nueva config

## Interfaz de Usuario (Pendiente)
⬜ Existe endpoint para listar dispositivos de un tenant
⬜ Existe endpoint para crear/actualizar/eliminar configuración de dispositivo
⬜ Existe endpoint para obtener comandas pendientes por dispositivo (pantalla de cocina)
⬜ Vista de tarjetas por pedido/orden
⬜ Polling HTMX para actualización automática
⬜ Filtro por tipo de producto
⬜ Notificación visual de nuevos pedidos