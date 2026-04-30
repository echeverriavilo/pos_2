# 014 - Vistas CRUD de backoffice

## Objetivo

Implementar vistas de gestion para las entidades operativas del tenant, incluyendo productos, categorias, roles, usuarios y formas de pago.

## Contexto

Esta tarea introduce el backoffice tenant para administrar catalogo, usuarios y configuraciones operativas desde la UI.

## Dependencias

- `002_catalogo_inventario_base.md`
- `006_roles_permisos_autorizacion.md`
- `012_mejoras_pago_y_formas_pago.md`

## Reglas aplicables

- las vistas deben respetar permisos por rol;
- toda operacion CRUD debe respetar el aislamiento por tenant;
- la UI debe apoyarse en services y no introducir logica de negocio propia.

## Plan de implementacion

- crear vistas, formularios y listados para entidades operativas del tenant;
- integrar validaciones de permisos y tenant;

## Criterios de aceptacion

- existen vistas CRUD operativas para las entidades definidas;
- las operaciones respetan permisos y tenant;
- los cambios realizados desde la UI persisten correctamente;

## Validacion requerida

- `pytest`

## Estado

Completado

## Notas y resultados

### Entidades implementadas

| Entidad | App | Permiso | Vistas |
|---------|-----|---------|--------|
| Categorias | catalog | `manage_inventory` | listar, crear, editar, pausar, inhabilitar |
| Productos | catalog | `manage_inventory` | listar (agrupado por categoria, busqueda), crear, editar, pausar, inhabilitar |
| Roles | core | `manage_users` | listar, crear, editar, pausar, inhabilitar |
| Usuarios | core | `manage_users` | listar, crear, editar, pausar, inhabilitar |
| Formas de pago | orders | `manage_cash_registers` | listar, crear, editar, pausar, inhabilitar |

### Patrones establecidos

- **Formularios**: Django ModelForms con widgets Bootstrap. Labels en espanol.
- **Vistas**: `@login_required` + `require_permission(user, permiso)`. Listas filtradas por `inhabilitado=False`. Operaciones delegadas a services.
- **Templates**: server-rendered, extienden `grastro/base.html`. Tablas Bootstrap responsive con acciones inline (editar link, pausar POST, inhabilitar POST con confirmacion JS).
- **Formato de numeros**: widget `CLPNumberInput` (sin decimales, punto como separador de miles). Template tag `|currency` para `$X.XXX`.
- **Modales HTMX**: boton `[+]` junto a selects FK abre modal con formulario de creacion rapida (categoria en producto, rol en usuario).

### Semantica de activacion

- **Pausar** (`is_active`/`activo`/`pausado`): reversible, elemento aparece al final de listas con badge "Pausado".
- **Inhabilitar** (`inhabilitado`): permanente, elemento no aparece en listas. Equivalente funcional a "eliminar" para el usuario.
- Para usuarios: `inhabilitado=True` + `is_active=False` bloquea login. `pausado=True` es solo marca visual.

### Tests

58 tests en 5 archivos. Cobertura: CRUD, permisos, tenant isolation, inhabilitar, pausar, busqueda, validacion de duplicados.

### Bugs corregidos durante implementacion

- `save(update_fields=['email'])` en `AbstractBaseUser` no persiste cambios al `USERNAME_FIELD`. Solucion: `user.save()` completo en `UserService.update_tenant_user`.
- `IntegrityError` al crear producto/categoria con nombre duplicado. Solucion: validacion explicita en servicios con `ValidationError`.
