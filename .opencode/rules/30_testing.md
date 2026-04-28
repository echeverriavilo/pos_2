# Regla Testing

## Objetivo

Los tests validan reglas de negocio, invariantes y flujos del sistema.

## Cobertura mínima

- Cada regla de negocio tiene al menos un test.
- Cada invariant relevante tiene cobertura.
- Cada flujo crítico definido en spec debe estar cubierto.

## Prioridades

1. Servicios y transiciones de estado.
2. Integración entre componentes con base de datos.
3. Flujos UI/HTMX cuando cambian comportamiento del sistema.

## Escenarios obligatorios

- apertura, pago y cierre de mesa;
- flujo rápido con confirmación post pago;
- pagos totales, abonos y pagos por productos;
- cálculo y aplicación de propina;
- generación de comandas por dispositivo;
- descuento y reversa de stock según flujo.

## Convención

- `test_<accion>_<condicion>_<resultado>`
