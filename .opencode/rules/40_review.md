# Regla Review

## Criterio de revisión

Validar siempre:

- alineación con `docs/spec_maestro.md`;
- respeto de invariantes;
- enforcement multitenant;
- atomicidad de operaciones críticas;
- ausencia de lógica de negocio en views/models/frontend;
- ausencia de side-effects ocultos;
- tests suficientes para el cambio.

## Hallazgos prioritarios

- regresiones de dominio;
- violaciones de permisos o tenant;
- transiciones de estado inválidas;
- inconsistencias de pago o stock;
- cobertura faltante en escenarios críticos.
