import sqlite3
import os
from database.connection import get_db_connection
from datetime import datetime


def inicializar_base_de_datos():
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'hunting_bot.db'))
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🧹 Base de datos antigua eliminada.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       phone
                       TEXT
                       PRIMARY
                       KEY,
                       whatsapp_id
                       TEXT
                       UNIQUE,
                       name
                       TEXT
                       NOT
                       NULL,
                       ghl_id
                       TEXT
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL,
                       status
                       TEXT
                       NOT
                       NULL
                       DEFAULT
                       'active',
                       created_at
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    # NUEVA: Tabla de estados para menús interactivos multitarea
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_states
                   (
                       phone
                       TEXT
                       PRIMARY
                       KEY,
                       state
                       TEXT
                       NOT
                       NULL,
                       data
                       TEXT
                   )
                   """)

    usuarios_iniciales = [
        ("51932068040", "206893205217341", "Rafael Sanchez TI", "PaTMhzFbNbsRTvE3os5o", "TI"),
        ("51957770680", None, "Humberto Benavides", "qOREYbNFDXYgi4ePmLT6", "CEO"),
        ("51934841065", None, "Mathias Villena TI", "51PrMSG3YMKkq0XlKdrY", "TI"),
        ("51916064524", None, "Administrador TI", "PaTMhzFbNbsRTvE3os5o", "TI")
    ]

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for phone, wa_id, name, ghl_id, role in usuarios_iniciales:
        cursor.execute(
            "INSERT INTO users (phone, whatsapp_id, name, ghl_id, role, status, created_at) VALUES (?, ?, ?, ?, ?, 'active', ?)",
            (phone, wa_id, name, ghl_id, role, ahora)
        )

    conn.commit()
    conn.close()
    print("✅ Tablas estructuradas (users + user_states) con éxito.")


if __name__ == "__main__":
    inicializar_base_de_datos()