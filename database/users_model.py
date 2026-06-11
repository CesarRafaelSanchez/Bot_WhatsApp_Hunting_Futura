import sqlite3
from database.connection import get_db_connection
from datetime import datetime

def get_user_by_identifier(identifier: str):
    """Busca un usuario activo que coincida con el teléfono o con el whatsapp_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT phone, whatsapp_id, name, ghl_id, role, status FROM users 
        WHERE (phone = ? OR whatsapp_id = ?) AND status = 'active'
        """,
        (identifier, identifier)
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_ghl_id(ghl_id: str):
    """Busca un usuario activo basándose en su ID de GHL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT phone, whatsapp_id, name, ghl_id, role, status FROM users 
        WHERE ghl_id = ? AND status = 'active'
        """,
        (ghl_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(phone: str, whatsapp_id: str, name: str, ghl_id: str, role: str):
    """Registra un nuevo usuario con ambas identificaciones."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (phone, whatsapp_id, name, ghl_id, role, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (phone, whatsapp_id, name, ghl_id, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_user_status(phone: str, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE phone = ?", (status, phone))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def get_user_by_phone_only(phone: str):
    """Busca un usuario activo estrictamente por su número celular."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, ghl_id, role, status, whatsapp_id FROM users WHERE phone = ? AND status = 'active'", (phone,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_whatsapp_id(phone: str, whatsapp_id: str):
    """Inyecta el ID comercial de 15 dígitos automáticamente en la primera interacción."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET whatsapp_id = ? WHERE phone = ?", (whatsapp_id, phone))
    conn.commit()
    conn.close()

def update_user_role(phone: str, role: str):
    """Modifica el Rol de un usuario usando su celular o su whatsapp_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE phone = ? OR whatsapp_id = ?", (role, phone, phone))
    conn.commit()
    conn.close()

def set_simulation(ti_phone: str, simulated_phone: str):
    """Establece una simulación activa para el usuario TI."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO simulations (ti_phone, simulated_phone) VALUES (?, ?)
        ON CONFLICT(ti_phone) DO UPDATE SET simulated_phone = excluded.simulated_phone
    """, (ti_phone, simulated_phone))
    conn.commit()
    conn.close()

def get_simulated_user(ti_phone: str):
    """Retorna el teléfono del usuario que el TI está simulando."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT simulated_phone FROM simulations WHERE ti_phone = ?", (ti_phone,))
    row = cursor.fetchone()
    conn.close()
    return row["simulated_phone"] if row else None

def clear_simulation(ti_phone: str):
    """Elimina la simulación activa para el usuario TI."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM simulations WHERE ti_phone = ?", (ti_phone,))
    conn.commit()
    conn.close()

def get_ti_users_simulating(simulated_phone: str):
    """Obtiene los usuarios TI que están simulando a un gestor específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.phone, u.whatsapp_id 
        FROM simulations s
        JOIN users u ON (s.ti_phone = u.phone OR s.ti_phone = u.whatsapp_id)
        WHERE s.simulated_phone = ?
    """, (simulated_phone,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]