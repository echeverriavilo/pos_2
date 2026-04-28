# Regla Backend

## Arquitectura

- El backend es la única fuente de verdad.
- La lógica de negocio vive en `services/`.
- `selectors/` solo leen datos; no mutan estado.
- Views y templates no toman decisiones de dominio.

## Restricciones

- No signals para lógica crítica.
- No side-effects ocultos en ORM.
- Cada operación crítica debe ser explícita y trazable.
- Multitenancy obligatorio en queries, validaciones y relaciones.
- `platform_staff` solo puede bypassar tenant mediante lógica explícita del servicio.

## Atomicidad

Usar `transaction.atomic` en:

- creación de órdenes;
- pagos;
- transiciones de estado;
- movimientos de inventario;
- cualquier operación que combine varias mutaciones del dominio.

## Estilo de servicio

- Nombres de funciones explícitos.
- Validar input, ejecutar lógica y retornar resultado claro.
- Docstrings en español cuando la función tenga comportamiento relevante.
