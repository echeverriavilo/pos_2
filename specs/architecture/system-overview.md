# System Overview

## Architecture Style

- Monolito modular
- Backend centrado en dominio
- Frontend server-rendered con HTMX

---

## Core Components

### Backend (Django)

Responsable de:

- lógica de negocio
- persistencia
- validación de reglas
- control de estados

---

### Frontend (Templates + HTMX)

Responsable de:

- renderización de UI
- interacción del usuario
- representación de estados

---

### Database (PostgreSQL)

Responsable de:

- persistencia de datos
- integridad estructural

---

## Interaction Flow

1. Usuario interactúa con UI
2. HTMX o request HTTP llama al backend
3. Backend ejecuta lógica en services
4. Se actualiza estado en base de datos
5. Backend responde con HTML parcial o completo
6. UI se actualiza

---

## Domain Authority

El backend es la única fuente de verdad.

- El frontend no toma decisiones
- La base de datos no contiene lógica

---

## State Consistency

Toda transición debe:

- pasar por lógica de dominio
- respetar invariants
- ser validada antes de persistir

---

## Constraints

- No microservicios
- No lógica distribuida
- No duplicación de reglas

---

## Success Criteria

El sistema es consistente si:

- el dominio controla todas las decisiones
- el frontend solo representa estado
- no existen side-effects ocultos