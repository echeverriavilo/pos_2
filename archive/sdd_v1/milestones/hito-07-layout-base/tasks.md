# Hito 07 - Tasks

## Tareas

1. [x] Descargar Bootstrap 5 local (CSS + JS + Fonts)
2. [x] Crear base.html con estructura PWA
3. [x] Implementar sidebar de navegación
4. [x] Agregar toasts de feedback
5. [x] Hacer responsive para móvil
6. [x] Crear módulos vacíos (urls placeholder)
7. [x] Configurar login/logout personalizados
8. [x] Crear template login.html (independiente)
9. [x] Crear dashboard con cards
10. [ ] Verificar flujo completo: login → dashboard → logout

---

## Detalle de Tareas Completadas

### 1. Bootstrap 5 + Icons
- static/vendor/bootstrap/5.3/bootstrap.min.css
- static/vendor/bootstrap/5.3/bootstrap.bundle.min.js
- static/vendor/bootstrap-icons/bootstrap-icons.css
- static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff

### 2. base.html
- Estructura HTML5 con meta viewport PWA
- Sidebar responsivo (collapse en móvil)
- Toasts container para feedback
- Contenedor principal

### 3. Sidebar
- Navegación con iconos Bootstrap
- Links a: Productos, Categorías, Mesas, Órdenes, Nuevo Pedido, Historial, Configuración
- Responsive: collapse en móvil, expandido en desktop

### 4. Toasts
- Sistema de mensajes Django (messages framework)
- Tipos: success, error, warning, info
- Posición: bottom-right

### 5. Responsive
- Breakpoint: 767.98px
- Mobile: sidebar oculto, menu hamburguesa
- Desktop: sidebar expandido

### 6. Módulos
- apps/catalog/ → productos, categorías
- apps/dining/ → mesas
- apps/orders/ → órdenes, nuevo pedido, historial
- apps/core/ → configuración

### 7. Autenticación
- LOGIN_URL = '/login/' en settings.py
- LOGOUT_URL = '/logout/'
- LOGIN_REDIRECT_URL = '/'

### 8. Login Template
- Template independiente (sin base.html)
- Formulario Bootstrap
- Mensajes de error

### 9. Dashboard
- Grid de cards (Bootstrap)
- Links a todos los módulos
- Categorizados: Catálogo, Salón, Órdenes, Administración