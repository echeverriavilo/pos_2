# Decisions Log

## Entry Format

- Fecha
- Contexto
- Decisión
- Justificación
- Impacto

---

## Entries

- Fecha: 2026-04-10
  - Contexto: Hito 01 exige aislamiento por tenant_id, autenticación operativa y soporte para staff de plataforma.
  - Decisión: crear el dominio `apps.core` con modelos `Tenant`, `Role`, `Membership`, `StaffTenantAccess` y `CustomUser`; resolver tenant por subdominio con middleware/tenant_context y forzar filtros adicionales en managers.
  - Justificación: el sistema debe asegurar aislamiento a nivel ORM y base de datos, mientras que los usuarios de soporte necesitan acceso controlado a múltiples tenants.
  - Impacto: las consultas quedan automáticamente limitadas por el tenant actual, los roles base (`administrador`, `cajero`, `garzón`) se siembran en la creación de tenant y queda soportado el login rápido por PIN sin comprometer la seguridad general.

- Fecha: 2026-04-12
  - Contexto: Hito 02 presentó el catálogo e inventario tenant-aware y necesitaba garantizar que el stock se mantuviera consistente para cada tenant.
  - Decisión: crear los modelos `Category`, `Product`, `Ingredient` y `StockMovement` con `TenantAwareManager`, implementar `InventoryService` con métodos separados por tipo de movimiento (ingreso/ajuste/venta) y mantener `Product.stock_actual` actualizado en transacciones atómicas, evitando stock negativo en productos inventariables.
  - Justificación: se requería un histórico confiable de movimientos, consultas rápidas al stock actual sin cálculos dinámicos y respeto al aislamiento por tenant.
  - Impacto: se documenta el flujo de inventario, se prepara la infraestructura para futuros hitos y se mantiene la consistencia entre movimientos y el stock persistido.

- Fecha: 2026-04-13
  - Contexto: Hito 3 formalizó la relación entre mesas y órdenes, con nuevas apps `dining` y `orders` que integran selectores, servicios y flujo de estados.
  - Decisión: conceptuar "order activo" como los estados ABIERTO, PAGADO_PARCIAL y CONFIRMADO, delegar la creación de órdenes a `orders.services.create_order_for_table`, y dejar documentadas las invariantes/responsabilidades del servicio de mesas (estado de mesa vs. orden) para facilitar el OrderBatch/Comanda del hito 4.
  - Justificación: mantener la propiedad de invariantes en `DiningTableService` y separar la creación de órdenes permite escalar el flujo hacia el motor de órdenes sin mezclar responsabilidades.
  - Impacto: la infraestructura queda organizada para el próximo hito, los selectores y servicios comparten la definición de estados activos y se documenta la necesidad futura de un modelo OrderBatch/Comanda.

- Fecha: 2026-04-12
  - Contexto: Hito 2 definió catálogo e inventario y necesitaba asegurar que el stock se mantuviera consistente por tenant y con históricos de movimientos.
  - Decisión: crear los modelos `Category`, `Product`, `Ingredient` y `StockMovement` con `TenantAwareManager`, implementar `InventoryService` con métodos separados por tipo de movimiento (ingreso, ajuste, venta) y mantener `Product.stock_actual` actualizado en transacciones, bloqueando stock negativo cuando corresponda.
  - Justificación: el inventario debe consultar fácilmente `stock_actual` sin cálculos dinámicos y los movimientos deben quedar registrados en un histórico verificable por tenant.
  - Impacto: se garantiza aislamiento de tenants en el catálogo/inventario, se documenta la necesidad de transacciones atómicas y se prepara el terreno para usar `InventoryService` en hitos futuros.

- Fecha: 2026-04-13
  - Contexto: Hito 3 formalizó la relación entre mesas y órdenes, además de crear las apps `dining` y `orders` necesarias para sostener la lógica.
  - Decisión: registrar en el log la creación de las apps `dining` y `orders`, el servicio `create_order_for_table` y los selectores que filtran mesas/órdenes activas; documentar la lista de estados válidos y las invariantes de `DiningTableService`.
  - Justificación: al mover orden explícitamente a `orders.services`, se facilita la evolución del motor de órdenes en el hito 4 y se mantiene la separación de responsabilidades entre servicios y selectores.
  - Impacto: la infraestructura queda organizada para el próximo hito y el log ya refleja las decisiones clave que acompañan a las nuevas apps.

- Fecha: 2026-04-13
  - Contexto: Hito 04 requiere un motor completo de órdenes con ítems, transiciones específicas por flujo y consistencia multitenant.
  - Decisión: ampliar `apps.orders` con el modelo `OrderItem` (con tenant forzado), selectores dedicados y un servicio central que exponga `create_order`, `add_item`, `remove_item`, `recalculate_total` y `transition_order_state`, manteniendo en español los docstrings que describen cada paso.
  - Justificación: el dominio exige que toda entidad pertenezca a un tenant y que los flujos de mesa/rápido transiten solo por estados permitidos; centralizar la lógica en servicios garantiza transacciones atómicas y facilita la integración futura con pagos y stock.
  - Impacto: se garantiza la consistencia de total bruto y estados, se documentan las reglas en el servicio y los tests, y se deja trazabilidad de la decisión en el log del execution tracking.

- Fecha: 2026-04-15
  - Contexto: Hito 06 requiere sistema de roles y permisos con validación en todos los servicios existentes.
  - Decisión: crear modelos `Permission` y `RolePermission` (tabla pivot), crear servicios de autorización `validate_tenant_access` y `validate_role_permission`, integrar validaciones en todos los servicios de orders/payments/dining añadiendo parámetro `user` obligatorio.
  - Justificación: specs definen que platform_staff debe tener bypass de tenant pero no de permisos; los permisos son explícitos (no herencia); la validación debe ocurrir en servicios, no en views.
  - Impacto: todos los servicios ahora requieren `user` y validan tenant y permisos; 43 tests actualizados y pasando; milestone completo.

- Fecha: 2026-04-15
  - Contexto: Hito 07 requiere layout base PWA, sidebar responsivo, toasts system y navegación funcional entre módulos. Además se necesita sistema de autenticación personalizado.
  - Decisión: descargar Bootstrap 5 + Bootstrap Icons localmente en static/vendor/, crear base.html con sidebar responsivo y toasts, configurar STATICFILES_DIRS y TEMPLATES DIRS en settings.py, crear templates mínimos para cada módulo (catalog, dining, orders, core), implementar login_view/logout_view personalizados con formulario Bootstrap, crear dashboard con grid de cards.
  - Justificación: specs definen HTML server-rendered con HTMX básico, Bootstrap instalación local (no CDN), mobile-first, diseño responsive con breakpoints; login redirect a /login/ porque no existían URLs de autenticación.
  - Impacto: Layout base funcional con sidebar responsivo, toasts para feedback, templates por módulo, login/logout personalizados con redirect a dashboard.

- Fecha: 2026-04-15
  - Contexto: El usuario accedió a localhost:8000/ y fue redirigido a /accounts/login/ (404) porque no existían URLs de autenticación configuradas.
  - Decisión: Agregar LOGIN_URL='/login/', LOGOUT_URL='/logout/', LOGIN_REDIRECT_URL='/' en settings.py; crear vistas login_view y logout_view en apps/core/views.py con autenticación Django; agregar rutas en apps/core/urls.py; crear template login.html independiente (sin base.html) para evitar loop de autenticación.
  - Justificación: El @login_required decorador redirige a LOGIN_URL configurada; el template de login debe ser independiente porque el usuario no está autenticado aún.
  - Impacto: Login funcional con formulario Bootstrap, logout cierra sesión y redirecciona a /login/, flujo completo: login → dashboard → módulos → logout.

- Fecha: 2026-04-15
  - Contexto:Sidebar no se despliega en móvil (solo iconos, no texto) y falta header superior con usuario/notificaciones/logout.
  - Decisión: Reescribir base.html con sidebar sin clase inicial collapsed-md (siempre expandido en desktop), usar clase .mobile-open solo para móvil, crear top-header con dropdown de usuario (configuración, logout), actualizar grastro.css con reglas responsive.
  - Justificación:El sidebar debe mostrarse siempre expandido en desktop; en móvil usar toggle class .mobile-open; el dropdown de usuario requiere autenticación active para mostrarse.
  - Impacto:Sidebar funciona en móvil y desktop, header superior con usuario, dropdown paraconfiguración y logout visible cuando autenticado.

- Fecha: 2026-04-15
  - Contexto: Error "VariableDoesNotExist: Failed lookup for key [username]" al renderizar base.html porque CustomUser no tiene campo username (usa email como USERNAME_FIELD).
  - Decisión: Agregar método get_short_name() a CustomUser que retorna first_name si existe, o email.split('@')[0] como fallback.
  - Justificación: CustomUser extiende de AbstractBaseUser pero no tiene campo username (el campo es email); el template espera get_short_name().
  - Impacto: Template ahora puede usar {{ user.get_short_name }} sin errores; dropdown muestra nombre de usuario o primer parte del email.

---

## Hito 09 - Mapa de Salón y Gestión de Mesas

- Fecha: 2026-04-16
  - Contexto: Necesitábamos un modal vertical para garzones en celulares (flujo de agregar nuevo pedido a mesa ocupada).
  - Decisión: Implementar como side panel que desliza desde la derecha (90% ancho en móvil) en lugar de modal centrado tradicional.
  - Justificación: Mejor experiencia táctil, acceso más rápido a elementos, optimizado para pantalla pequeña.
  - Impacto: Side panel con transitions CSS, scroll interno, diseño mobile-first.

- Fecha: 2026-04-16
  - Contexto: Necesitábamos acumular productos antes de confirmar el pedido completo.
  - Decisión: Carrito temporal en estado de JavaScript (no persistente) que se vacía al cancelar.
  - Justificación: Experiencia instantánea sin requests adicionales, comportamiento natural de cancelar al cerrar.
  - Impacto: JS maneja estado local, muestra detalle en footer antes de confirmar.

- Fecha: 2026-04-16
  - Contexto: Al agregar productos a mesa en estado PAGANDO, debía volver a OCUPADA según flujo definido en flows.md.
  - Decisión: Llamar directamente al método existente `DiningTableService.reopen_table()` en lugar de duplicar lógica.
  - Justificación: Consistencia con el código base, reutilización de validaciones existentes.
  - Impacto: Transición automática PAGANDO→OCUPADA al confirmar pedido.

- Fecha: 2026-04-16
  - Contexto: Necesitábamos layout responsive que funcionara en móvil sin ocupar toda la pantalla.
  - Decisión: Contenedor principal con flex column (categorías | productos | carrito detalle) con altura fija y overflow interno.
  - Justificación: Scroll nativo en secciones específicas, evita problemas de altura total de pantalla.
  - Impacto: CSS con max-height en footer, overflow-y:auto en body del side panel.

- Fecha: 2026-04-16
  - Contexto: Elementos con clase Bootstrap d-flex mostraban altura de 100vh inadvertidamente.
  - Decisión: Reemplazar `.d-flex` genérico por `.app-layout` específico en grastro.css y base.html.
  - Justificación: Regla CSS genérica afectaba todos los elementos Bootstrap, causando layout roto.
  - Impacto: Layout funciona correctamente en todas las vistas.

---

## Hito 11 - Módulo de Pagos y Cierre de Cuenta

- Fecha: 2026-04-16
  - Contexto: Hito 11 requería procesamiento visual de pagos parciales con desglose de IVA/propina, selector de items, y cierre de cuenta.
  - Decisión: Introducir `total_cuenta = total_bruto + propina_monto` como total a pagar. Actualizar `TransactionSelector.total_pending()` y todas las validaciones para usar este total. Condición de completado: `total_paid >= total_cuenta`.
  - Justificación: El acceptance criteria exige desglose completo donde "total" incluye propina, comportamiento natural de un POS gastronómico.
  - Impacto: `update_order_payment_state` ahora compara contra `total_cuenta`, `total_pending` incluye propina, pago TOTAL cubre propina automáticamente.

- Fecha: 2026-04-16
  - Contexto: Review post-implementación detectó que `propina_selector.html` destruía el modal al fijar propina porque retornaba solo el desglose parcial.
  - Decisión: `orden_fijar_propina` ahora retorna el modal completo (`modal_pago.html`) en lugar de solo `desglose_cuenta.html`.
  - Justificación: HTMX reemplaza el target completo, si solo retorna el desglose se pierden las pestañas de pago.
  - Impacto: Modal se mantiene íntegro tras cambiar propina, usuario puede continuar pagando.

- Fecha: 2026-04-16
  - Contexto: `selector_items_pago.html` usaba `DOMContentLoaded` que no se dispara tras swap de HTMX.
  - Decisión: Script ahora usa `htmx:afterSwap` además de `DOMContentLoaded`, con función reutilizable `initItemSelector(container)`.
  - Justificación: HTMX no dispara DOMContentLoaded al hacer swap de contenido dinámico.
  - Impacto: Checkboxes de pago por productos calculan subtotal correctamente tras cualquier actualización HTMX.

- Fecha: 2026-04-16
  - Contexto: `cuenta_actualizada.html` mostraba `precio_unitario_snapshot` en vez de `get_total` para cada item.
  - Decisión: Cambiar a `item.get_total` para mostrar subtotal (cantidad × precio).
  - Justificación: Inconsistencia visual con `pre_cuenta.html` y `selector_items_pago.html` que usan `get_total`.
  - Impacto: Cuenta muestra correctamente el subtotal de cada item.

- Fecha: 2026-04-17
  - Contexto: Todos los formularios de pago con `hx-post` y `hx-include` generaban errores CSRF en modales Bootstrap porque el token no se propagaba correctamente dentro del DOM del modal.
  - Decisión: Reemplazar todos los `hx-post` de formularios de pago con `fetch()` nativo, obteniendo CSRF desde `<meta name="csrf-token">`. Funciones centralizadas: `getCsrfToken()`, `paymentFetch()`, `submitTotalPayment()`, `submitAbono()`, `submitProductsPayment()`, `applyTip()`.
  - Justificación: HTMX con `hx-include` no encontraba el campo CSRF cuando el formulario estaba dentro de un modal Bootstrap dinámico. `fetch()` con token de meta tag elimina el problema de scoping.
  - Impacto: Todos los pagos (TOTAL, ABONO, PRODUCTOS) y propinas funcionan sin errores CSRF en ambos flujos (mesa y terminal).

- Fecha: 2026-04-17
  - Contexto: Las vistas `orden_procesar_pago` y `orden_fijar_propina` debían seleccionar template diferente según si la orden pertenece a una mesa o es de flujo rápido.
  - Decisión: Usar `order.table_id` para determinar el template: si existe → `modal_pago.html`, si es None → `terminal_modal_pago.html`. Aplicado en los 3 `render()` de `orden_procesar_pago` y en `orden_fijar_propina`.
  - Justificación: Flujo de mesa y flujo rápido tienen templates diferentes con estructura distinta. Antes usaban template hardcodeado o variable `table` faltante causando NoReverseMatch.
  - Impacto: Ambos flujos funcionan correctamente con su template correspondiente. Variable `table` disponible en todos los contextos.

- Fecha: 2026-04-17
  - Contexto: Al abrir el modal de pago, la propina aparecía en $0 sin sugerencia, obligando al usuario a calcular y aplicar manualmente.
  - Decisión: Cuando `order.propina_monto == 0`, los modales `mesa_modal_pago` y `terminal_modal_pago` auto-aplican la propina sugerida del 10% llamando a `set_tip()` al cargar.
  - Justificación: En la mayoría de los restaurantes chilenos se aplica propina del 10% por defecto. El usuario puede modificarla o quitarla, pero no debería empezar en $0.
  - Impacto: Propina 10% se calcula y muestra automáticamente al abrir modal de pago. Usuario puede editar con % o $ personalizados, o cancelar edición.

- Fecha: 2026-04-17
  - Contexto: La barra de acciones de mesa usaba `position: fixed` que se solapaba con el sidebar en desktop y causaba problemas de z-index.
  - Decisión: Cambiar a `position: sticky; bottom: 0` dentro de `.content-area` con `z-index` apropiado.
  - Justificación: Sticky positioning respeta el layout del sidebar y no requiere cálculos de offset manuales. Se comporta correctamente en desktop y móvil.
  - Impacto: Barra de acciones visible sin solapar sidebar, consistente en ambos viewports.

- Fecha: 2026-04-17
  - Contexto: `mesa_liberar_mesa` llamaba `set_table_paying()` que transicionaba a PAGANDO en lugar de cerrar la mesa correctamente.
  - Decisión: Cambiar a `release_table()` que transiciona a LIBRE, cerrando la mesa sin movimientos pendientes. Cambiar redirect de `/ordenes/mesa/{id}/` a `/salon/mesas/`.
  - Justificación: Liberar mesa debe ponerla en LIBRE, no PAGANDO. El redirect debe llevar al mapa de mesas, no a la orden que ya se cerró.
  - Impacto: Mesas se liberan correctamente y usuario es redirigido al mapa de mesas.

- Fecha: 2026-04-17
  - Contexto: `orden_procesar_pago` solo verificaba `Order.States.COMPLETADO` como condición de completado, pero el flujo rápido transiciona a CONFIRMADO (no COMPLETADO).
  - Decisión: Cambiar condición a `Order.States.COMPLETADO or Order.States.CONFIRMADO`.
  - Justificación: El flujo rápido marca la orden como CONFIRMADO al completar pago, no COMPLETADO. Sin este cambio, el modal no se cerraba ni redirigía correctamente.
  - Impacto: Ambos flujos (mesa y rápido) cierran correctamente tras pago completo.

- Fecha: 2026-04-17
  - Contexto: `propina_selector.html` usaba un modal Bootstrap anidado dentro de otro modal, causando problemas de z-index y scroll.
  - Decisión: Eliminar el modal anidado y reemplazar con edición inline: botones para % personalizado y $ fijo que muestran input directo dentro del selector.
  - Justificación: Modales anidados en Bootstrap tienen problemas conocidos de z-index y focus trap. La edición inline es más simple y natural en mobile.
  - Impacto: Propina se edita inline sin modales anidados, mejor UX en desktop y mobile.