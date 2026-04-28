# Tasks — Hito 01

1. Inicializar proyecto Django

2. Configurar PostgreSQL

3. Crear modelo Tenant

4. Crear Custom User (extensión de Django auth)

5. Implementar relación User ↔ Tenant

6. Crear modelo Role

7. Implementar roles dinámicos por tenant
   - carga inicial de roles base

8. Implementar autenticación:
   - email/password (Django auth)
   - login por PIN asociado a usuario
   
9. Implementar middleware de tenant

10. Forzar aislamiento por tenant en queries

11. Crear migraciones

12. Implementar tests:
    - autenticación
    - aislamiento de datos
    - relación user-tenant

13. Validar ejecución completa sin errores