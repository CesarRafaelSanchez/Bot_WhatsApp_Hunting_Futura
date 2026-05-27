import sqlite3
import os

# Forzamos la ruta absoluta real en el sistema
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hunting_bot.db'))

def get_db_connection():
    """Establece una conexión con la base de datos y retorna filas tipo diccionario."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn