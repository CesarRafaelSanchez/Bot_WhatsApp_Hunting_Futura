from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# REEMPLAZA ESTO CON TU API KEY DE GHL (V2 o de Ubicación)
GHL_API_KEY = "pit-91efad56-ae58-41d7-85f6-6b66504b7e16"


@app.route('/webhook-ghl', methods=['POST'])
def ghl_webhook():
    payload = request.json

    # 1. Extraemos la lista de URLs del campo mapeado
    urls_archivo = payload.get("Subir de Archivo 309h", [])

    if urls_archivo:
        url_privada = urls_archivo[0]
        print(f"\n[+] Intentando descargar desde: {url_privada}")

        # 2. Configuramos las cabeceras de autenticación de GHL
        headers = {
            "Authorization": f"Bearer {GHL_API_KEY}",
            "Version": "2021-04-15"  # Versión estándar de la API v2 de GHL
        }

        # 3. Hacemos la petición para descargar los bytes de la imagen
        response = requests.get(url_privada, headers=headers)

        if response.status_code == 200:
            # 4. Guardamos el archivo localmente para verificar que no esté corrupto
            with open("imagen_descargada.png", "wb") as f:
                f.write(response.content)
            print("[✓] ¡Imagen descargada con éxito como 'imagen_descargada.png'!")
        else:
            print(f"[X] Falló la descarga. Código de estado: {response.status_code}")
            print(f"Respuesta del servidor: {response.text}")
    else:
        print("\n[-] No se encontró ninguna URL en el campo 'Subir de Archivo 309h'")

    return jsonify({"status": "processed"}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)