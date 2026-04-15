# AGENTS.md - Gastropos

## Stack
- Django 5.2 + PostgreSQL
- pytest + pytest-django

## Comandos

```bash
# Tests
pytest

# Un archivo de test
pytest apps/orders/tests/test_services.py

# Check de Django
python manage.py check

# Servidor desarrollo
python manage.py runserver

# Migraciones
python manage.py migrate
python manage.py makemigrations
```

## Estructura

```
apps/
├── core/      # User, tenant, membership
├── catalog/   # Productos, ingredientes, stock
├── dining/    # Mesas
└── orders/    # Órdenes, pagos, transacciones
```

Cada app: `models/`, `services/`, `selectors/`, `tests/`

## Metodología SDD

Todo debe estar definido en `specs/` antes de implementar. Specs clave:
- `specs/domain/business-rules.md`
- `specs/domain/invariants.md`
- `specs/engineering/testing.md`

## Convenciones

- **Código**: Inglés
- **Docs/Comentarios**: Español
- **Timezone**: America/Santiago
- Tests: `test_<acción>_<condición>_<resultado>`
- Sin lógica de negocio en views/models - usar services

## Entorno

Requiere archivo `.env` con credenciales PostgreSQL.

## Archivos clave

- `grastro/settings.py` - Configuración Django
- `pytest.ini` - Configuración de tests