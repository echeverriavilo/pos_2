Tarea: `014`

Archivo de tarea: `014_vistas_crud_backoffice.md`

Objetivo de esta ejecución: `Implementar vistas CRUD de backoffice para productos, categorías, roles, usuarios y formas de pago, con respeto de permisos y tenant.`

In scope: `Solo lo definido en la tarea 14 y sus dependencias directas.`

Out of scope: `Cualquier funcionalidad no definida en la tarea o en el spec maestro.`

Tipo de trabajo principal: `frontend y backend`

Restricciones adicionales: `cualquier decision no cerrada, detenerse y preguntar.`

Validaciones obligatorias: `pytest`

Contexto extra:

## Estado actual

La implementacion de la tarea 13 esta completada (144 tests pasando, `manage.py check` sin errores). El sistema tiene:
- **Cajas**: CRUD completo con apertura, cierre por medio de pago (2 pasos), movimientos manuales con signo y medio de pago, historial de cierres.
- **Pagos**: transacciones con propina por pago, formas de pago tenant-aware, validacion de CashSession abierta.
- **Catalogo**: productos y categorias base.
- **Roles y permisos**: sistema de autorizacion con permisos granulares por tenant.
- **Template tags**: `currency` ($X.XXX) y `get_item` en `apps/core/templatetags/currency.py`.
- **Backoffice**: no existe aun. Esta tarea introduce las vistas de administracion.

## Pendientes de definicion en la tarea

- Mapa exacto de vistas CRUD requeridas (listado, formulario, detalle por cada entidad).
- Filtros, busquedas y UX detallada por modulo.
- Integracion con sidebar/navegacion existente.

---

Trabaja esta tarea usando el SDD vigente del proyecto.

Antes de implementar:
1. Lee `AGENTS.md`.
2. Lee `docs/spec_maestro.md`.
3. Lee `docs/tareas/014_vistas_crud_backoffice.md`.
4. Lee solo la regla relevante en `.opencode/rules/`.

Durante la ejecución:
- ejecuta solo el alcance indicado;
- no inventes reglas de negocio, permisos ni transiciones;
- no uses `archive/sdd_v1/` como fuente primaria;
- si hay una ambigüedad material, detente y pregunta;
- respeta `services/`, `selectors/`, multitenancy, atomicidad y testing.

Al cerrar:
- resume qué cambiaste;
- indica qué validaste;
- indica pendientes o riesgos.
