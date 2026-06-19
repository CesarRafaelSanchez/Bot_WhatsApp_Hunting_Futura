import sqlite3
import os
from database.connection import get_db_connection, DB_PATH
from datetime import datetime


def inicializar_base_de_datos():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"🧹 Base de datos antigua eliminada en: {DB_PATH}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar la DB: {e}")

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

    # NUEVA: Tabla de simulaciones para rol TI
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS simulations
                   (
                       ti_phone
                       TEXT
                       PRIMARY
                       KEY,
                       simulated_phone
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    usuarios_iniciales = [
        ("51932068040", None, "Rafael Sanchez TI", "PaTMhzFbNbsRTvE3os5o", "TI"),
        ("51957770680", "80754579107843", "Humberto Benavides", "qOREYbNFDXYgi4ePmLT6", "HUNTER"),
        ("51934841065", "169917999485122", "Mathias Villena TI", "51PrMSG3YMKkq0XlKdrY", "TI"),
        ("51918371086", "271901813375023", "Jean Pierre", "UzEVMjDvEHlw6YUAj3aJ", "HUNTER"),
        ("51992417859", None, "Jean Pierre Requelme Veliz", "biTnxEO9lNsTxJfOaUQM", "HUNTER")
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