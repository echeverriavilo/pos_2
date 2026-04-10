# Roles y Permisos

## Modelo de Roles

Cada tenant define sus propios usuarios.

### Roles Base

#### Administrador

Permisos:

- Configuración del local
- Gestión de usuarios
- Gestión de catálogo
- Gestión de inventario
- Acceso a reportes financieros

---

#### Cajero

Permisos:

- Procesamiento de pagos
- Apertura de caja
- Cierre de caja
- Gestión de transacciones parciales

---

#### Garzón

Permisos:

- Gestión de mesas
- Creación de pedidos
- Adición de productos
- Solicitud de pre-cuenta

Restricciones:

- No puede anular productos pagados
- No puede anular productos sin autorización si no está configurado

---

## Sistema de Permisos

- Cada tenant puede activar/desactivar permisos específicos por rol
- Los permisos son configurables