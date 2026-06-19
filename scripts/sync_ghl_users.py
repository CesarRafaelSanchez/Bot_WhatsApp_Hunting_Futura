import os
import sys
import re
import requests
from datetime import datetime

# Agregar la raíz del proyecto al sys.path para poder importar config y database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from database.connection import get_db_connection

def normalize_phone(phone: str) -> str:
    if not phone:
        return None
    # Eliminar todos los caracteres no numéricos
    cleaned = re.sub(r'\D', '', phone)
    if not cleaned:
        return None
    
    # Formato de Perú: si tiene 9 dígitos y empieza con 9, anteponer 51
    if len(cleaned) == 9 and cleaned.startswith('9'):
        return '51' + cleaned
        
    # Si tiene 11 dígitos y empieza con 51, ya está normalizado
    if len(cleaned) == 11 and cleaned.startswith('51'):
        return cleaned

    return cleaned

def get_role_by_name(name: str) -> str:
    name_clean = name.strip().lower()
    
    # Rol TI
    if name_clean in ["mathias villena ti", "rafael sanchez ti"]:
        return "TI"
    
    # Rol CEO
    if name_clean in ["humberto benavides presidencia", "humberto benavides"]:
        return "CEO"
        
    # Rol Back Office
    if name_clean in ["alexander watson huamani", "stefano sotomarino goche"]:
        return "BACKOFFICE"
        
    # Por defecto
    return "HUNTER"

def sync_users():
    print("[INFO] Iniciando sincronizacion de usuarios desde GoHighLevel...")
    
    # 1. Obtener usuarios actuales de la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT phone, ghl_id, name, role FROM users")
    existing_users = cursor.fetchall()
    
    existing_phones = {row['phone'] for row in existing_users if row['phone']}
    existing_ghl_ids = {row['ghl_id'] for row in existing_users if row['ghl_id']}
    
    print(f"[BD] Usuarios actuales en BD: {len(existing_users)}")
    for row in existing_users:
        print(f"   - {row['name']} | Telefono: {row['phone']} | GHL ID: {row['ghl_id']} | Rol: {row['role']}")
        
    # 2. Consultar usuarios en GoHighLevel API
    headers = {
        "Authorization": f"Bearer {config.GHL_TOKEN}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    url = f"https://services.leadconnectorhq.com/users/?locationId={config.LOCATION_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[ERROR] Error al consultar GHL: {response.status_code} - {response.text}")
            return
        
        ghl_users = response.json().get("users", [])
        print(f"[GHL] Usuarios encontrados en GHL: {len(ghl_users)}")
        
    except Exception as e:
        print(f"[ERROR] Error en la peticion a GHL: {e}")
        return
        
    # 3. Procesar e insertar nuevos usuarios
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevos_usuarios = []
    
    for ghl_user in ghl_users:
        ghl_id = ghl_user.get("id")
        name = ghl_user.get("name")
        ghl_phone = ghl_user.get("phone")
        
        if not ghl_id:
            continue
            
        normalized_phone = normalize_phone(ghl_phone)
        role = get_role_by_name(name)
        
        # Verificar si el usuario ya existe por ID o por Telefono
        if ghl_id in existing_ghl_ids:
            print(f"[OMITIR] Omitiendo (ya existe por GHL ID): {name} ({ghl_id})")
            continue
            
        if normalized_phone and normalized_phone in existing_phones:
            print(f"[OMITIR] Omitiendo (ya existe por Telefono {normalized_phone}): {name}")
            continue
            
        if not normalized_phone:
            print(f"[ALERTA] El usuario {name} no tiene un telefono valido. Se omitira para evitar conflictos en WhatsApp.")
            continue
            
        # Registrar para insercion
        print(f"[AGREGAR] Programado para agregar: {name} | Telefono: {normalized_phone} | GHL ID: {ghl_id} | Rol: {role}")
        nuevos_usuarios.append((normalized_phone, None, name, ghl_id, role, 'active', ahora))

    # 4. Insertar en la Base de Datos
    if nuevos_usuarios:
        try:
            cursor.executemany(
                """
                INSERT INTO users (phone, whatsapp_id, name, ghl_id, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                nuevos_usuarios
            )
            conn.commit()
            print(f"[BD] Se agregaron {len(nuevos_usuarios)} nuevos usuarios a la base de datos con exito.")
        except Exception as e:
            print(f"[ERROR] Error al guardar en base de datos: {e}")
            conn.rollback()
    else:
        print("[INFO] No se encontraron nuevos usuarios para agregar.")
        
    conn.close()
    print("[INFO] Sincronizacion completada.")

if __name__ == "__main__":
    sync_users()
