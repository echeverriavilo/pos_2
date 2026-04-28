# AGENTS.md - Gastropos

## Stack

- Django 5.2 + PostgreSQL
- Django Templates + HTMX + Bootstrap local
- pytest + pytest-django

## Comandos esenciales

```bash
pytest
pytest apps/orders/tests/test_services.py
python manage.py check
python manage.py runserver
python manage.py migrate
python manage.py makemigrations
```

## Estructura real del repo

```text
apps/       # apps Django de dominio
grastro/    # settings, urls y plantillas base
static/     # assets locales
docs/       # SDD canónico
.opencode/  # reglas operativas para OpenCode
```

Cada app Django debe usar `models/`, `services/`, `selectors/`, `tests/`.

## Principios no negociables

- La fuente canónica del dominio es [docs/spec_maestro.md](/d:/ia_dev/pos_2/grastro_pos/docs/spec_maestro.md).
- No inventar reglas de negocio ni transiciones fuera de spec.
- No poner lógica de negocio en views ni models; usar services.
- Operaciones críticas: atómicas con `transaction.atomic`.
- Multitenancy obligatorio: toda operación se filtra por tenant, salvo `platform_staff` controlado explícitamente.
- Código en inglés; comentarios y docstrings en español.
- Timezone obligatoria: `America/Santiago`.
- Los tests validan reglas de negocio, invariantes y flujos, no solo implementación.

## Qué leer primero

- Tarea nueva o ambigua: `docs/spec_maestro.md`
- Trabajo acotado: archivo relevante en `docs/tareas/`
- Implementación backend: `.opencode/rules/10_backend.md`
- Implementación frontend: `.opencode/rules/20_frontend.md`
- Testing: `.opencode/rules/30_testing.md`
- Review: `.opencode/rules/40_review.md`

## Archivo canónico

- Producto, dominio, arquitectura e ingeniería: [docs/spec_maestro.md](/d:/ia_dev/pos_2/grastro_pos/docs/spec_maestro.md)
- Tareas atómicas: [docs/tareas](/d:/ia_dev/pos_2/grastro_pos/docs/tareas)
- Decisiones persistentes: [docs/historial/decisiones.md](/d:/ia_dev/pos_2/grastro_pos/docs/historial/decisiones.md)
