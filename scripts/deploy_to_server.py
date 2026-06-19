import paramiko
import os
import time
import sys

HOST = "100.112.88.76"
USER = "soporte_futura_main"
PASS = "Futura2026!"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print(f"Conectando a {HOST} vía SSH...")
try:
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
    print("¡Conexión SSH exitosa!")
except Exception as e:
    print(f"Error conectando por SSH: {e}")
    sys.exit(1)

# 1. Encontrar el directorio del proyecto
print("Buscando el directorio del proyecto en el servidor...")
stdin, stdout, stderr = ssh.exec_command("find /home/soporte_futura_main /var/www /opt -maxdepth 4 -name Bot_WhatsApp_Hunting_Futura -type d 2>/dev/null")
paths = stdout.read().decode().strip().split("\n")
project_path = None
for p in paths:
    if p and "Bot_WhatsApp_Hunting_Futura" in p:
        project_path = p
        break

if not project_path:
    print("No se pudo encontrar la carpeta 'Bot_WhatsApp_Hunting_Futura' en el servidor.")
    ssh.close()
    sys.exit(1)

print(f"Directorio encontrado en: {project_path}")

# 2. Transferir archivos usando SFTP
print("Iniciando transferencia de archivos SFTP...")
sftp = ssh.open_sftp()

files_to_upload = [
    "app.py",
    "bot/menus.py",
    "bot/router.py",
    "database/users_model.py",
    "database/init_db.py"
]

local_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

for file_rel_path in files_to_upload:
    local_path = os.path.join(local_base, file_rel_path.replace("/", os.sep))
    remote_path = f"{project_path}/{file_rel_path}"
    print(f"  Subiendo {file_rel_path} -> {remote_path} ...")
    try:
        sftp.put(local_path, remote_path)
        print("    [OK]")
    except Exception as e:
        print(f"    [ERROR] {e}")

sftp.close()

# 3. Ejecutar actualizaciones en la base de datos de producción
print("Ejecutando sentencias SQLite en producción...")
db_path = f"{project_path}/hunting_bot.db"

sql_commands = [
    # Crear tabla de simulaciones
    f"sqlite3 {db_path} \"CREATE TABLE IF NOT EXISTS simulations (ti_phone TEXT PRIMARY KEY, simulated_phone TEXT NOT NULL);\"",
    # Corregir Typo Jean Pierre
    f"sqlite3 {db_path} \"UPDATE users SET phone = '51918371086' WHERE phone = '51918371068';\"",
    # Actualizar datos de Rafael Sanchez TI
    f"sqlite3 {db_path} \"UPDATE users SET phone = '51932068040', status = 'active' WHERE name = 'Rafael Sanchez TI';\""
]

for cmd in sql_commands:
    print(f"  Ejecutando: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.read().decode().strip()
    if err:
        print(f"    [Advertencia/Error SQLite]: {err}")
    else:
        print("    [Ejecutado correctamente]")

# 4. Reiniciar la aplicación usando Docker Compose
print("Reiniciando la aplicación vía Docker Compose...")
restart_cmd = f"cd {project_path} && docker compose down && docker compose up -d --build"
print(f"  Ejecutando: {restart_cmd}")
stdin, stdout, stderr = ssh.exec_command(restart_cmd)
err_out = stderr.read().decode().strip()
std_out = stdout.read().decode().strip()
if err_out:
    print(f"  [Detalle/Advertencia Docker]:\n{err_out}")
if std_out:
    print(f"  [Salida Docker]:\n{std_out}")
print("  Aplicación reiniciada con éxito vía Docker Compose.")

ssh.close()
print("Despliegue completado con éxito.")
