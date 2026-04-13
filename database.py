import sqlite3
from pathlib import Path


def _sqlite_path():
    base_dir = Path(__file__).resolve().parent
    return str(base_dir / "kirakira_local.db")


def _table_exists(conn, table_name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _column_exists(conn, table_name, column_name):
    if not _table_exists(conn, table_name):
        return False

    cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(col[1] == column_name for col in cols)


def _fondo_fecha_unique_legacy(conn):
    if not _table_exists(conn, "fondo_caja"):
        return False

    table_sql_row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'fondo_caja'"
    ).fetchone()
    table_sql = (table_sql_row[0] or "").upper() if table_sql_row else ""
    if "FECHA TEXT NOT NULL UNIQUE" in table_sql:
        return True

    indexes = conn.execute("PRAGMA index_list(fondo_caja)").fetchall()
    for _, idx_name, is_unique, *_ in indexes:
        if not is_unique:
            continue

        idx_cols = conn.execute(f"PRAGMA index_info({idx_name})").fetchall()
        col_names = [row[2] for row in idx_cols]
        if col_names == ["fecha"]:
            return True

    return False


def _rebuild_fondo_caja(conn):
    conn.execute("ALTER TABLE fondo_caja RENAME TO fondo_caja_legacy")
    conn.execute("""
        CREATE TABLE fondo_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL DEFAULT 0,
            tienda_id INTEGER,
            FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
        )
    """)
    conn.execute("""
        INSERT INTO fondo_caja (id, fecha, monto, tienda_id)
        SELECT id, fecha, monto, COALESCE(tienda_id, 1)
        FROM fondo_caja_legacy
    """)
    conn.execute("DROP TABLE fondo_caja_legacy")


def _ensure_sqlite_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tiendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    conn.execute("INSERT OR IGNORE INTO tiendas (id, nombre) VALUES (1, 'Tienda 1')")
    conn.execute("INSERT OR IGNORE INTO tiendas (id, nombre) VALUES (2, 'Tienda 2')")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            tienda_id INTEGER,
            FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
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
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            tienda_id INTEGER,
            FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
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
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            tienda_id INTEGER,
            FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS fondo_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL DEFAULT 0,
            tienda_id INTEGER,
            FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
        )
    """)

    if _fondo_fecha_unique_legacy(conn):
        _rebuild_fondo_caja(conn)

    if not _column_exists(conn, "usuarios", "tienda_id"):
        conn.execute("ALTER TABLE usuarios ADD COLUMN tienda_id INTEGER")

    if not _column_exists(conn, "ventas", "tienda_id"):
        conn.execute("ALTER TABLE ventas ADD COLUMN tienda_id INTEGER")

    if not _column_exists(conn, "gastos_caja", "tienda_id"):
        conn.execute("ALTER TABLE gastos_caja ADD COLUMN tienda_id INTEGER")

    if not _column_exists(conn, "fondo_caja", "tienda_id"):
        conn.execute("ALTER TABLE fondo_caja ADD COLUMN tienda_id INTEGER")

    conn.execute("""
        UPDATE usuarios
        SET tienda_id = 1
        WHERE UPPER(rol) IN ('EMPLEADO', 'VENDEDOR') AND tienda_id IS NULL
    """)
    conn.execute("""
        UPDATE usuarios
        SET tienda_id = 1
        WHERE usuario = 'Empleado1'
    """)
    conn.execute("""
        UPDATE usuarios
        SET tienda_id = 2
        WHERE usuario = 'Vendedor2'
    """)

    conn.execute("UPDATE ventas SET tienda_id = 1 WHERE tienda_id IS NULL")
    conn.execute("UPDATE gastos_caja SET tienda_id = 1 WHERE tienda_id IS NULL")
    conn.execute("UPDATE fondo_caja SET tienda_id = 1 WHERE tienda_id IS NULL")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_tienda_id ON usuarios(tienda_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ventas_tienda_fecha ON ventas(tienda_id, fecha)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_gastos_tienda_fecha ON gastos_caja(tienda_id, fecha)")
    conn.execute("DROP INDEX IF EXISTS idx_fondo_fecha_tienda")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_fondo_fecha_tienda ON fondo_caja(fecha, tienda_id)"
    )

    conn.commit()


def get_connection():
    conn = sqlite3.connect(_sqlite_path())
    _ensure_sqlite_schema(conn)
    return conn
