import os
import traceback
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from database import get_connection

app = Flask(__name__)
app.secret_key = "kirakira_secret_key"

def get_db_connection():
    conn = sqlite3.connect("kirakira_local.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def home():
    return render_template("login.html")


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_connection()
        conn.close()
        return "Conexion exitosa usando SQLite"
    except Exception as e:
        print(traceback.format_exc())
        return f"Error de conexion: {repr(e)}"


@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/empleado-dashboard")
def empleado_dashboard():
    return render_template("empleado_dashboard.html")

from datetime import datetime

@app.route("/cierre_caja", methods=["GET", "POST"])
def cierre_caja():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    if request.method == "POST":
        monto = float(request.form["monto"])

        cursor.execute("""
            SELECT id FROM fondo_caja
            WHERE fecha = ?
        """, (fecha_hoy,))
        existente = cursor.fetchone()

        if existente:
            cursor.execute("""
                UPDATE fondo_caja
                SET monto = ?
                WHERE fecha = ?
            """, (monto, fecha_hoy))
        else:
            cursor.execute("""
                INSERT INTO fondo_caja (fecha, monto)
                VALUES (?, ?)
            """, (fecha_hoy, monto))

        conn.commit()

    cursor.execute("""
        SELECT id, total, metodo_pago, fecha
        FROM ventas
        WHERE DATE(fecha) = DATE('now', 'localtime')
        ORDER BY fecha DESC
    """)
    ventas_hoy = cursor.fetchall()

    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) AS total_vendido
        FROM ventas
        WHERE DATE(fecha) = DATE('now', 'localtime')
    """)
    total_vendido = cursor.fetchone()["total_vendido"]

    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) AS total_gastos
        FROM gastos_caja
        WHERE DATE(fecha) = DATE('now', 'localtime')
    """)
    total_gastos = cursor.fetchone()["total_gastos"]

    balance_neto = total_vendido - total_gastos

    cursor.execute("""
        SELECT monto
        FROM fondo_caja
        WHERE fecha = ?
    """, (fecha_hoy,))
    fondo_hoy = cursor.fetchone()

    monto_fondo = fondo_hoy["monto"] if fondo_hoy else 0

    conn.close()

    return render_template(
        "cierre_caja.html",
        ventas_hoy=ventas_hoy,
        total_vendido=total_vendido,
        total_gastos=total_gastos,
        balance_neto=balance_neto,
        monto_fondo=monto_fondo
    )

@app.route("/consultar-productos")
def consultar_productos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nombre, codigo, precio, stock, categoria
        FROM productos
        WHERE activo = 1
        ORDER BY id
    """
    )
    productos = cursor.fetchall()

    conn.close()
    return render_template("consultar_productos.html", productos=productos)


@app.route("/caja")
def caja():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nombre, codigo, precio, stock, categoria
        FROM productos
        WHERE activo = 1
        ORDER BY nombre
    """
    )
    productos = cursor.fetchall()
    conn.close()

    carrito = session.get("carrito", [])
    total = sum(item["subtotal"] for item in carrito)

    return render_template(
        "caja.html",
        productos=productos,
        carrito=carrito,
        total=total,
    )


@app.route("/agregar-al-carrito", methods=["POST"])
def agregar_al_carrito():
    conn = get_connection()
    cursor = conn.cursor()

    producto_id = request.form["producto_id"]
    cantidad = int(request.form["cantidad"])

    cursor.execute(
        """
        SELECT id, nombre, precio, stock
        FROM productos
        WHERE id = ?
    """,
        (producto_id,),
    )
    producto = cursor.fetchone()
    conn.close()

    if not producto:
        return "Producto no encontrado"

    if cantidad <= 0:
        return "La cantidad debe ser mayor a 0"

    if cantidad > producto[3]:
        return f"No hay suficiente stock. Disponible: {producto[3]}"

    carrito = session.get("carrito", [])
    subtotal = producto[2] * cantidad

    carrito.append(
        {
            "producto_id": producto[0],
            "nombre": producto[1],
            "precio": producto[2],
            "cantidad": cantidad,
            "subtotal": subtotal,
        }
    )

    session["carrito"] = carrito
    return redirect(url_for("caja"))


@app.route("/eliminar-del-carrito/<int:index>")
def eliminar_del_carrito(index):
    carrito = session.get("carrito", [])

    if 0 <= index < len(carrito):
        carrito.pop(index)

    session["carrito"] = carrito
    return redirect(url_for("caja"))


@app.route("/finalizar-venta", methods=["POST"])
def finalizar_venta():
    carrito = session.get("carrito", [])

    if not carrito:
        return "El carrito esta vacio"

    metodo_pago = request.form["metodo_pago"]
    conn = get_connection()
    cursor = conn.cursor()
    total = sum(item["subtotal"] for item in carrito)

    cursor.execute(
        """
        INSERT INTO ventas (total, metodo_pago)
        VALUES (?, ?)
    """,
        (total, metodo_pago),
    )
    venta_id = cursor.lastrowid

    for item in carrito:
        cursor.execute(
            """
            INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                venta_id,
                item["producto_id"],
                item["cantidad"],
                item["precio"],
                item["subtotal"],
            ),
        )

        cursor.execute(
            """
            UPDATE productos
            SET stock = stock - ?
            WHERE id = ?
        """,
            (item["cantidad"], item["producto_id"]),
        )

    conn.commit()
    conn.close()

    session["carrito"] = []
    return redirect(url_for("caja"))


@app.route("/ventas_del_dia")
@app.route("/ventas-dia")
def ventas_del_dia():
    if "usuario" not in session:
        return redirect(url_for("home"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, total, metodo_pago, fecha
        FROM ventas
        WHERE DATE(fecha) = DATE('now', 'localtime')
        ORDER BY fecha DESC
    """
    )
    ventas_hoy = cursor.fetchall()

    cursor.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM ventas
        WHERE DATE(fecha) = DATE('now', 'localtime')
    """
    )
    total_vendido = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COALESCE(SUM(monto), 0)
        FROM gastos_caja
        WHERE DATE(fecha) = DATE('now', 'localtime')
    """
    )
    total_gastos = cursor.fetchone()[0]
    balance_neto = total_vendido - total_gastos

    conn.close()

    return render_template(
        "ventas_dia.html",
        ventas_hoy=ventas_hoy,
        total_vendido=total_vendido,
        total_gastos=total_gastos,
        balance_neto=balance_neto,
    )


@app.route("/gastos-caja", methods=["GET", "POST"])
def gastos_caja():
    conn = get_connection()
    cursor = conn.cursor()
    mensaje = ""

    if request.method == "POST":
        concepto = request.form["concepto"]
        monto = request.form["monto"]

        cursor.execute(
            """
            INSERT INTO gastos_caja (concepto, monto)
            VALUES (?, ?)
        """,
            (concepto, monto),
        )
        conn.commit()
        mensaje = "Gasto guardado correctamente"

    cursor.execute(
        """
        SELECT id, concepto, monto, fecha
        FROM gastos_caja
        WHERE DATE(fecha) = DATE('now', 'localtime')
        ORDER BY id DESC
    """
    )
    gastos = cursor.fetchall()

    cursor.execute(
        """
        SELECT COALESCE(SUM(monto), 0)
        FROM gastos_caja
        WHERE DATE(fecha) = DATE('now', 'localtime')
    """
    )
    total_gastos = cursor.fetchone()[0]

    conn.close()
    return render_template(
        "gastos_caja.html",
        gastos=gastos,
        total_gastos=total_gastos,
        mensaje=mensaje,
    )


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    password = request.form["password"]

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND password = ?",
            (usuario, password),
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return "Usuario o contrasena incorrectos"

        rol = user[4]
        session["usuario"] = user[2]
        session["rol"] = rol

        if rol == "Administrador":
            return redirect(url_for("admin_dashboard"))
        if rol == "Empleado":
            return redirect(url_for("empleado_dashboard"))
        return f"Rol no reconocido: {rol}"

    except Exception as e:
        print(traceback.format_exc())
        return f"Error en login: {repr(e)}"


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5055"))
    app.run(debug=True, port=port, use_reloader=False)
