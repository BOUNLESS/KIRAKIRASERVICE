# KIRAKIRA Rebuild

Sistema de Punto de Venta (POS) multi-tienda desarrollado con Flask y SQLite para la gestión de ventas, inventario, gastos y reportes administrativos.

---

## Características Principales

- Autenticación de usuarios y roles

- Arquitectura multi-tienda

- Gestión de inventario

- Punto de venta con carrito de compras

- Control automático de stock

- Registro de gastos de caja
  
- Ventas del día

- Fondo y cierre de caja

- Balance general administrativo

- Exportación de reportes a Excel

---

## Tecnologías Utilizadas

* Python
* Flask
* SQLite
* OpenPyXL
* HTML
* CSS
* Jinja2

---

## Capturas de Pantalla

### Inicio de Sesión

<img width="1918" height="943" alt="KIRAKIRA LOGIN" src="https://github.com/user-attachments/assets/940b66ca-334e-4098-ab03-a11317dee310" />

Pantalla de autenticación para administradores y empleados.

---

### Caja / Punto de Venta

<img width="1899" height="938" alt="CAJATIENDAKIRAKIRA" src="https://github.com/user-attachments/assets/f7b83097-eda5-42ef-85a1-2ff1fd6d8090" />

Módulo principal de ventas con carrito de compras y selección de método de pago.

---

### Gestión de Inventario

<img width="1919" height="941" alt="INVENTARIOKIRAKIRA" src="https://github.com/user-attachments/assets/a00c103e-5022-4c92-abd1-a0c4813212a0" />

Administración de productos, stock y movimientos de inventario por tienda.

---

### Balance General

<img width="1918" height="943" alt="BALANCEKIRAKIRA" src="https://github.com/user-attachments/assets/02adf973-4697-4366-b38e-6f349b6d639f" />

Panel administrativo con ventas, gastos y utilidad neta por tienda.

---

### Exportación a Excel

<img width="1897" height="780" alt="EXCELKIRAKIRA" src="https://github.com/user-attachments/assets/f842d1e8-0eb0-4ce7-9096-9123227bc190" />

Generación automática de reportes en Excel para análisis y control administrativo.

---

## Estado del Proyecto

### Módulos Completados

* Login y autenticación
* Roles de usuario
* Arquitectura multi-tienda
* Inventario
* Caja y carrito de ventas
* Registro de ventas
* Control automático de stock
* Gastos de caja
* Fondo y cierre de caja
* Balance general
* Exportación de reportes a Excel

### Próximas Funcionalidades

* Dashboard con gráficas
* Reportes PDF
* Migración a PostgreSQL
* Mejoras de UI/UX
* Auditoría de movimientos
* Estadísticas avanzadas

---

## Arquitectura

* `app.py` → Aplicación principal y rutas
* `database.py` → Conexión y gestión de base de datos
* `templates/` → Vistas HTML
* `static/` → Archivos CSS
* `kirakira_local.db` → Base de datos SQLite

---

## Instalación

```bash
git clone <URL_DEL_REPOSITORIO>
cd KIRAKIRA-Rebuild

python -m venv .venv
pip install -r requirements.txt

python app.py
```

La aplicación estará disponible en:

```text
http://127.0.0.1:5055
```

---

## Aprendizajes

Durante el desarrollo de este proyecto trabajé con:

* Desarrollo web con Flask
* Diseño de bases de datos relacionales
* Arquitectura multi-tienda
* Gestión de sesiones y autenticación
* Manejo de inventarios
* Control de ventas y caja
* Reportes administrativos
* Exportación de archivos Excel con OpenPyXL

---

## Autor

### Ricardo Boone

Estudiante de Ingeniería en Software

Tecnologías principales:
Python • Flask • SQLite • PostgreSQL • HTML • CSS • Git

---

Proyecto desarrollado como parte de mi portafolio personal y aprendizaje de desarrollo de software orientado a negocios reales.
