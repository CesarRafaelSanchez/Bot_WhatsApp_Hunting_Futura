import json
from database.connection import get_db_connection

def get_user_state(phone: str):
    """Recupera el estado actual de navegación del usuario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT state, data FROM user_states WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["state"], json.loads(row["data"]) if row["data"] else {}
    return None, {}

def set_user_state(phone: str, state: str, data: dict = None):
    """Guarda o actualiza el estado y los datos temporales del flujo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    data_json = json.dumps(data) if data else json.dumps({})
    cursor.execute("""
        INSERT INTO user_states (phone, state, data) VALUES (?, ?, ?)
        ON CONFLICT(phone) DO UPDATE SET state = excluded.state, data = excluded.data
    """, (phone, state, data_json))
    conn.commit()
    conn.close()

def clear_user_state(phone: str):
    """Borra el estado para regresar al flujo normal de menús."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_states WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()