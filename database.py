import sqlite3
from pathlib import Path


def _sqlite_path():
    base_dir = Path(__file__).resolve().parent
    return str(base_dir / "kirakira_local.db")


def _ensure_sqlite_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            categoria TEXT,
            activo INTEGER DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS venta_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS gastos_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()


def get_connection():
    conn = sqlite3.connect(_sqlite_path())
    _ensure_sqlite_schema(conn)
    return conn
