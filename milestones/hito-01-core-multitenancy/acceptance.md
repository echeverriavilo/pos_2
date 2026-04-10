# Acceptance Criteria — Hito 01

El hito se considera completado si:

- El proyecto Django corre sin errores
- PostgreSQL está configurado correctamente
- Existen modelos:
  - Tenant
  - User
  - Role
- Un usuario puede autenticarse
- Un usuario pertenece a un tenant
- No es posible acceder a datos de otro tenant
- Existen tests para:
  - autenticación
  - aislamiento de datos
- Todos los tests pasan
- Las migraciones se aplican correctamente