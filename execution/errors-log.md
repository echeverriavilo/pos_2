# Errors Log

## Purpose

Registrar errores relevantes que afecten decisiones futuras.

---

## Entry Format

- Fecha
- Error
- Contexto
- Causa
- Acción tomada

---

## Usage

El orchestrator debe:

- evitar repetir errores registrados
- ajustar decisiones en base a este historial

---

## Entries

- Fecha: 2026-04-10
  - Error: psycopg2 OperationalError al ejecutar `pytest` y `makemigrations` porque el usuario `postgres`/`postgres` no autenticaba en la base local.
  - Contexto: configuración inicial del proyecto cambiaba a PostgreSQL, pero la base `pos2` se creó y requiere credenciales de `pos2_ow`.
  - Causa: los settings estaban apuntando a credenciales equivocadas (`postgres`/`postgres`).
  - Acción tomada: actualicé `grastro/settings.py` para usar la base `pos2` y el usuario/contraseña correctos (`pos2_ow`/`1234`). Después de eso, `manage.py migrate` y `pytest` se ejecutan sin errores.

- Fecha: 2026-04-13
  - Error: ninguno (entorno estable tras los hitos 1-3).
  - Contexto: el desarrollo completó los hitos de multitenancy, inventario y mesas; no se detectaron nuevos bloqueos o errores significativos.
  - Causa: instancia estable y tests locales exitosos.
  - Acción tomada: se mantiene la vigilancia, pero no fue necesario actuar.

- Fecha: 2026-04-15
  - Error: Se marcó hito 06 como completo sin verificar acceptance criteria - roles sin permisos.
  - Contexto: Revisión post-implementación reveló que roles base se creaban pero no tenían permisos asignados.
  - Causa: No se revisó acceptance criteria antes de declarar completo; no se completó la tarea "Implementar reglas por rol".
  - Acción tomada: Se modificó TenantService._seed_roles() para asignar permisos automáticamente según ROLE_PERMISSIONS mapping, se creó migración 0004 para roles existentes. Tests actualizados y pasando (43).
