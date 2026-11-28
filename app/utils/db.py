"""
Helper de conexión a PostgreSQL.
Escribimos TODAS las queries a mano (sin ORM), como exige el subject.
"""

"""
Qué hace:
Encapsula la conexión a PostgreSQL. 
(encapsular significa que no se expone la conexión directamente, sino que se hace a través de funciones helper).
Usa psycopg2 y el cursor RealDictCursor para trabajar cómodamente con diccionarios.
    psycopg2 es la librería oficial de PostgreSQL para Python.
    RealDictCursor es un tipo de cursor (un objeto que permite ejecutar queries y obtener resultados)
    que devuelve los resultados como diccionarios en lugar de tuplas, 
    lo que hace que sea más fácil trabajar con los datos.
    Una queri es una instrucción SQL que se ejecuta en la base de datos, como SELECT, INSERT, UPDATE o DELETE.
Se puede usar con un context manager (with get_db() as conn:) que es un patrón de diseño que asegura que 
la conexión se cierre automáticamente al salir del bloque, o con la función execute() para queries simples.
Y todas las queries se escriben a mano (cumple el subject: no se usan ORMs).
"""

import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from flask import current_app, has_app_context


def get_db_url():
    """Devuelve la URL de conexión según el contexto."""
    if has_app_context():
        return current_app.config["DATABASE_URL"]
    return os.getenv(
        "DATABASE_URL",
        "postgresql://matcha:matcha_secret_change_me@db:5432/matcha",
    )


def get_connection():
    """Abre una nueva conexión a la base de datos."""
    return psycopg2.connect(
        get_db_url(),
        cursor_factory=psycopg2.extras.RealDictCursor,  # resultados como diccionarios
    )


@contextmanager
def get_db():
    """
    Context manager recomendado para usar la BD.
    Ejemplo:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ...", params)
                rows = cur.fetchall()
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(query, params=None, fetchone=False, fetchall=False):
    """
    Helper de conveniencia para queries simples.
    - fetchone=True  → devuelve un solo registro (dict o None)
    - fetchall=True  → devuelve lista de registros
    - sin flags      → devuelve el número de filas afectadas
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
            return cur.rowcount
