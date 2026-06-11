import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

HOST = "100.112.88.76"
USER = "soporte_futura_main"
PASS = "Futura2026!"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print(f"Conectando a {HOST} vía SSH...")
try:
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

nginx_conf = """
server {
    listen 80;
    server_name webhook.novacoresac.com;

    location /webhook/crm-notificaciones {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

nginx_conf = """
server {
    listen 80;
    server_name webhook.novacoresac.com;

    location /webhook/crm-notificaciones {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

stdin, stdout, stderr = ssh.exec_command("ps aux | grep cloudflare")
print(stdout.read().decode(errors='replace'))

ssh.close()
