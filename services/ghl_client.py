import requests
import config
import json
import io
import re
import os

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

HEADERS_GHL = {
    "Authorization": f"Bearer {config.GHL_TOKEN}",
    "Version": "2021-04-15",
    "Content-Type": "application/json"
}
BASE_URL = "https://services.leadconnectorhq.com"

FIELD_ID_MAP = {
    "z3oowb5sA1BCEUW1clPn": "tipo_via",
    "5Qj8ala9IQ2nZeUpyLWB": "inmobiliaria",
    "g0iB6S9D8nJukEjqvjkJ": "numeracion_via",
    "H9m1fipzTYGn6xB4ocxZ": "distrito",
    "G5tzckiDp4NSVjA4ZYxA": "coordenadas",
    "EESQxx49zXBuxyBb1KVk": "nombre_via",
    "qxHUg4a4BI5Wy8bY2inP": "foto_edificio",
}


def _get_url_from_value(val) -> str:
    if not val:
        return ""

    # 🛠️ GHL a veces manda la lista camuflada como string '["hash"]'
    if isinstance(val, str):
        val_str = val.strip()
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, list) and len(parsed) > 0:
                    val = parsed[0]
            except Exception:
                pass

    if isinstance(val, list) and len(val) > 0:
        val = val[0]

    if isinstance(val, dict):
        val = val.get("url") or val.get("value") or val.get("fieldValue") or val.get("downloadUrl") or ""

    val_str = str(val).strip()

    # 🚀 EXTRACTOR 1: Busca un link directo http/https
    match = re.search(r'(https?://[^\s\]"\'}]+)', val_str)
    if match:
        return match.group(1)

    # 🚀 EXTRACTOR 2: Si GHL mandó solo el ID del documento (como el código largo que encontraste)
    clean_val = re.sub(r'[^a-zA-Z0-9_-]', '', val_str)
    if len(clean_val) > 20:
        return f"https://services.leadconnectorhq.com/documents/download/{clean_val}"

    return ""


def _get_contact_details(contact_id: str):
    if not contact_id:
        return {}

    try:
        response = requests.get(f"{BASE_URL}/contacts/{contact_id}", headers=HEADERS_GHL)
        if response.status_code != 200:
            return {}
        return response.json().get("contact", {}) or {}
    except Exception as e:
        print(f"⚠️ Error cargando contacto {contact_id}: {e}")
        return {}


def _extract_project_fields(contact: dict) -> dict:
    tipo_via = ""
    nombre_via = ""
    numeracion_via = ""
    distrito = ""
    coordenadas = "No especificada"
    inmobiliaria = "No especificada"
    foto_edificio = None
    foto_montantes = None
    supervisor = ""
    ejecutivo = ""

    for field in contact.get("customFields", []) or []:
        value = field.get("value")

        # 🛠️ CORRECCIÓN CRÍTICA: GHL v2 usa 'fieldValue' en las Oportunidades en lugar de 'value'
        if value is None:
            value = field.get("fieldValue")

        if value is None or value == "" or value == []:
            continue

        field_id = field.get("id")
        field_key = str(field.get("key", "")).lower()
        field_name = str(field.get("name", "")).lower()
        normalized_value = str(value)

        if field_id in FIELD_ID_MAP:
            mapped = FIELD_ID_MAP[field_id]
            if mapped == "inmobiliaria":
                inmobiliaria = normalized_value
            elif mapped == "tipo_via":
                tipo_via = normalized_value
            elif mapped == "nombre_via":
                nombre_via = normalized_value
            elif mapped == "numeracion_via":
                numeracion_via = normalized_value
            elif mapped == "numeracion_via_alt" and not numeracion_via:
                numeracion_via = normalized_value
            elif mapped == "distrito":
                distrito = normalized_value
            elif mapped == "coordenadas":
                coordenadas = normalized_value
            elif mapped == "foto_edificio":
                val_url = _get_url_from_value(value)
                if val_url and val_url.startswith("http") and not foto_edificio:
                    foto_edificio = val_url
            elif mapped == "foto_montantes":
                val_url = _get_url_from_value(value)
                if val_url and val_url.startswith("http") and not foto_montantes:
                    foto_montantes = val_url
            continue

        if field_key == "cf_inmobiliaria":
            inmobiliaria = normalized_value
        elif field_key == "cf_tipo_via":
            tipo_via = normalized_value
        elif field_key == "cf_nombre_via":
            nombre_via = normalized_value
        elif field_key == "cf_numeracion_via":
            numeracion_via = normalized_value
        elif field_key == "cf_distrito":
            distrito = normalized_value
        elif field_key == "cf_coordenadas":
            coordenadas = normalized_value
        elif field_key in ["cf_supervisor_hunting", "cf_supervisor"] or "supervisor" in field_key or "supervisor" in field_name:
            supervisor = normalized_value
        elif field_key in ["cf_ejecutivo_principal", "cf_ejecutivo"] or "ejecutivo" in field_key or "ejecutivo" in field_name:
            ejecutivo = normalized_value
        elif "foto" in field_key or "foto" in field_name:
            val_url = _get_url_from_value(value)
            print(f"🕵️‍♂️ [EXTRACT] Evaluando campo '{field_name}' / '{field_key}' -> URL extraída: '{val_url}'",
                  flush=True)
            if "montante" in field_key or "montante" in field_name:
                if val_url and val_url.startswith("http") and not foto_montantes:
                    foto_montantes = val_url
            else:
                if val_url and val_url.startswith("http") and not foto_edificio:
                    foto_edificio = val_url

    if not distrito:
        for tag in contact.get("tags", []) or []:
            if isinstance(tag, str) and tag.lower().startswith("distrito:"):
                distrito = tag.split(":", 1)[1].strip()
                break

    return {
        "inmobiliaria": inmobiliaria,
        "tipo_via": tipo_via,
        "nombre_via": nombre_via,
        "numeracion_via": numeracion_via,
        "distrito": distrito,
        "coordenadas": coordenadas,
        "foto_edificio": foto_edificio,
        "foto_montantes": foto_montantes,
        "supervisor": supervisor,
        "ejecutivo": ejecutivo,
    }


def get_photos_from_ghl_system_api(opp_id: str, contact_id: str, project_name: str):
    import os
    import requests
    ghl_system_url = os.getenv("GHL_SYSTEM_API_URL", "http://localhost:5001")

    posibles_ids = [opp_id, contact_id, project_name]
    for identifier in posibles_ids:
        if not identifier:
            continue
        try:
            url = f"{ghl_system_url}/api/cache/{identifier}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                datos = resp.json()
                foto_edificio = None
                foto_montantes = None

                # 🚀 1. Intentamos usar las rutas de las imágenes locales guardadas en la caché de GHL_System
                path_edificio = datos.get("foto_edificio_path")
                path_montantes = datos.get("foto_montantes_path")

                if path_edificio:
                    filename_edificio = path_edificio.replace('\\', '/').split('/')[-1]
                    foto_edificio = f"{ghl_system_url}/api/cache/files/{filename_edificio}"
                    print(f"📸 [API CACHE BOT] Detectada foto edificio local en caché: {foto_edificio}", flush=True)

                if path_montantes:
                    filename_montantes = path_montantes.replace('\\', '/').split('/')[-1]
                    foto_montantes = f"{ghl_system_url}/api/cache/files/{filename_montantes}"
                    print(f"📸 [API CACHE BOT] Detectada foto montantes local en caché: {foto_montantes}", flush=True)

                # Fallback: Si no existen las rutas locales, usamos los enlaces originales de GHL
                if not foto_edificio:
                    val_edificio = datos.get("cf_foto_edificio")
                    if val_edificio:
                        if isinstance(val_edificio, list) and len(val_edificio) > 0:
                            foto_edificio = val_edificio[0]
                        elif isinstance(val_edificio, str):
                            foto_edificio = val_edificio

                if not foto_montantes:
                    val_montantes = datos.get("cf_foto_montantes")
                    if val_montantes:
                        if isinstance(val_montantes, list) and len(val_montantes) > 0:
                            foto_montantes = val_montantes[0]
                        elif isinstance(val_montantes, str):
                            foto_montantes = val_montantes

                return foto_edificio, foto_montantes
        except Exception as e:
            print(f"⚠️ Error al conectar con API de GHL_System para '{identifier}': {e}", flush=True)
    return None, None


def get_cached_details_from_ghl_system_api(opp_id: str, contact_id: str, project_name: str) -> dict:
    import os
    import requests
    ghl_system_url = os.getenv("GHL_SYSTEM_API_URL", "http://localhost:5001")

    posibles_ids = [opp_id, contact_id, project_name]
    for identifier in posibles_ids:
        if not identifier:
            continue
        try:
            url = f"{ghl_system_url}/api/cache/{identifier}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"⚠️ Error al conectar con API de GHL_System para '{identifier}': {e}", flush=True)
    return {}


def _build_opportunity_summary(opp: dict, fetch_details: bool = False) -> dict:
    stage_id = opp.get("pipelineStageId", "")
    contact = opp.get("contact", {}) or {}
    contact_id = opp.get("contactId") or contact.get("id")

    cf_contact = contact.get("customFields", []) or []
    cf_opp = opp.get("customFields", []) or []

    # 🛠️ OPTIMIZACIÓN CRÍTICA: Solo hacemos la llamada si fetch_details=True
    if fetch_details and contact_id and not cf_contact and not cf_opp:
        fetched_contact = _get_contact_details(contact_id)
        if fetched_contact:
            contact = fetched_contact

    # Consolidar todos los custom fields
    contact["customFields"] = (contact.get("customFields", []) or []) + cf_opp

    fields = _extract_project_fields(contact)
    direccion_parts = []
    if fields["tipo_via"]:
        direccion_parts.append(fields["tipo_via"])
    if fields["nombre_via"]:
        direccion_parts.append(fields["nombre_via"])
    if fields["numeracion_via"]:
        direccion_parts.append(fields["numeracion_via"])
    if fields["distrito"]:
        direccion_parts.append(fields["distrito"])

    direccion = " ".join(direccion_parts) if direccion_parts else "No especificada"

    foto_edificio = fields["foto_edificio"]
    foto_montantes = fields["foto_montantes"]
    supervisor = fields["supervisor"]
    ejecutivo = fields["ejecutivo"]

    # 🚀 PRIORIDAD CACHÉ LOCAL: Buscamos siempre primero las fotos locales en GHL_System para evitar URLs purgadas
    if fetch_details:
        import os
        cache_data = get_cached_details_from_ghl_system_api(opp.get("id"), contact_id, opp.get("name"))
        if cache_data:
            path_edificio = cache_data.get("foto_edificio_path")
            path_montantes = cache_data.get("foto_montantes_path")
            ghl_system_url = os.getenv("GHL_SYSTEM_API_URL", "http://localhost:5001")
            if path_edificio:
                filename_edificio = path_edificio.replace('\\', '/').split('/')[-1]
                foto_edificio = f"{ghl_system_url}/api/cache/files/{filename_edificio}"
            if path_montantes:
                filename_montantes = path_montantes.replace('\\', '/').split('/')[-1]
                foto_montantes = f"{ghl_system_url}/api/cache/files/{filename_montantes}"

            if not supervisor:
                supervisor = cache_data.get("cf_supervisor_hunting") or cache_data.get("cf_supervisor") or cache_data.get("supervisor") or ""
            if not ejecutivo:
                ejecutivo = cache_data.get("cf_ejecutivo_principal") or cache_data.get("cf_ejecutivo") or cache_data.get("ejecutivo") or ""

    return {
        "id": opp.get("id"),
        "name": opp.get("name", "Sin Nombre").upper(),
        "direccion": direccion,
        "inmobiliaria": fields["inmobiliaria"],
        "foto": foto_edificio,
        "foto_edificio": foto_edificio,
        "foto_montantes": foto_montantes,
        "coordenadas": fields["coordenadas"],
        "stage": stage_id,
        "contact_id": contact_id,
        "supervisor": supervisor,
        "ejecutivo": ejecutivo,
    }



def _search_opportunities(params: dict, fetch_details: bool = False) -> list:
    try:
        response = requests.get(f"{BASE_URL}/opportunities/search", headers=HEADERS_GHL, params=params)
        if response.status_code != 200:
            return []

        opps = response.json().get("opportunities", [])
        return [_build_opportunity_summary(opp, fetch_details) for opp in opps]
    except Exception as e:
        print(f"⚠️ Error GHL Search: {e}")
        return []


def get_opportunities_by_user(ghl_user_id: str):
    """Obtiene y formatea las oportunidades operativas activas para el Hunter (Opción 1 - Límite 100)."""
    params = {
        "location_id": config.LOCATION_ID,
        "pipeline_id": config.PIPELINE_ID,
        "assigned_to": ghl_user_id,
        "limit": 100,
    }
    # 🚀 FAST FETCH: Listados sin detalles pesados para evitar timeout
    return _search_opportunities(params, fetch_details=False)


def get_opportunities_advanced(ghl_user_id: str, search_query: str = None, stage_id: str = None):
    """Consulta avanzada en GHL v2 filtrando por query o etapa específica (Opción 4 - Límite 20)."""
    params = {
        "location_id": config.LOCATION_ID,
        "pipeline_id": config.PIPELINE_ID,
        "assigned_to": ghl_user_id,
        "limit": 20,
    }

    if search_query:
        params["q"] = search_query

    if stage_id:
        params["pipeline_stage_id"] = stage_id

    # ⏳ SLOW FETCH: Trae todos los detalles porque se muestran directamente
    return _search_opportunities(params, fetch_details=True)


def enrich_opportunity(opp_summary: dict) -> dict:
    """Carga los detalles faltantes (custom fields) bajo demanda para una sola oportunidad."""
    contact_id = opp_summary.get("contact_id")
    opp_id = opp_summary.get("id")

    print(f"🚀 [ENRICH] Iniciando búsqueda de fotos para Opp ID: {opp_id}", flush=True)
    if not contact_id and not opp_id:
        return opp_summary

    contact = _get_contact_details(contact_id) if contact_id else {}

    # 🛠️ RECUPERAR CAMPOS DE LA OPORTUNIDAD: Aquí está guardada la foto,
    # y no venía en la carga rápida (Lazy Load) por defecto.
    cf_opp = []
    ff_opp = []
    if opp_id:
        try:
            # 🛠️ EXIGIMOS A GHL QUE INCLUYA LOS CUSTOM FIELDS
            params_opp = {"location_id": config.LOCATION_ID, "include": "customFields,formFields"}

            resp = requests.get(f"{BASE_URL}/opportunities/{opp_id}", headers=HEADERS_GHL, params=params_opp)

            print(f"🚀 [ENRICH] Respuesta de GHL (Status): {resp.status_code}", flush=True)
            if resp.status_code == 200:
                opp_data = resp.json().get("opportunity") or resp.json()

                print("🧪 [DEBUG OPP] Keys oportunidad:", list(opp_data.keys()), flush=True)
                print("🧪 [DEBUG OPP] Custom Fields:", flush=True)
                for cf in opp_data.get("customFields", []) or []:
                    print({
                        "id": cf.get("id"),
                        "key": cf.get("key"),
                        "name": cf.get("name"),
                        "value": cf.get("value"),
                        "fieldValue": cf.get("fieldValue"),
                    }, flush=True)

                print("🧪 [DEBUG OPP] Form Fields:", flush=True)
                for ff in opp_data.get("formFields", []) or []:
                    print({
                        "id": ff.get("id"),
                        "key": ff.get("key"),
                        "name": ff.get("name"),
                        "value": ff.get("value"),
                        "fieldValue": ff.get("fieldValue"),
                    }, flush=True)

                cf_opp = opp_data.get("customFields", []) or []
                ff_opp = opp_data.get("formFields", []) or []

                # 🛠️ FALLBACK: Si GHL aplana los campos directamente en el objeto
                for k, v in opp_data.items():
                    k_lower = k.lower()
                    if k in FIELD_ID_MAP or "foto" in k_lower or "archivo" in k_lower:
                        if not any(cf.get("id") == k for cf in cf_opp):
                            cf_opp.append({"id": k, "name": k, "fieldValue": v})

            else:
                print(f"⚠️ [ENRICH] Falló la petición a GHL: {resp.text}", flush=True)
        except Exception as e:
            print(f"⚠️ Error cargando oportunidad completa: {e}", flush=True)

    print("🧪 [DEBUG CONTACT] Custom Fields del Contacto:", flush=True)
    for cf in contact.get("customFields", []) or []:
        print({
            "id": cf.get("id"),
            "key": cf.get("key"),
            "name": cf.get("name"),
            "value": cf.get("value"),
            "fieldValue": cf.get("fieldValue"),
        }, flush=True)

    # 🛠️ SUMAMOS TODO AL ESCÁNER: Custom Fields (Contact + Opp) + Form Fields (Contact + Opp)
    contact["customFields"] = (contact.get("customFields", []) or []) + cf_opp + ff_opp + (
                contact.get("formFields", []) or [])

    fields = _extract_project_fields(contact)
    print(f"🚀 [ENRICH] Foto final encontrada en GHL: {fields.get('foto_edificio')}", flush=True)
    direccion_parts = [p for p in
                       [fields["tipo_via"], fields["nombre_via"], fields["numeracion_via"], fields["distrito"]] if p]

    opp_summary["direccion"] = " ".join(direccion_parts) if direccion_parts else "No especificada"
    opp_summary["inmobiliaria"] = fields["inmobiliaria"]
    opp_summary["coordenadas"] = fields["coordenadas"]

    foto_edificio = fields.get("foto_edificio")
    foto_montantes = fields.get("foto_montantes")
    supervisor = fields.get("supervisor")
    ejecutivo = fields.get("ejecutivo")

    # 🚀 PRIORIDAD CACHÉ LOCAL: Buscamos siempre primero las fotos locales en la caché de GHL_System para evitar URLs de GHL muertas
    print(f"🔍 [CACHE GHL_SYSTEM] Buscando fotos locales en caché para: {opp_summary.get('name')}", flush=True)
    cache_data = get_cached_details_from_ghl_system_api(opp_id, contact_id, opp_summary.get("name"))
    if cache_data:
        path_edificio = cache_data.get("foto_edificio_path")
        path_montantes = cache_data.get("foto_montantes_path")
        ghl_system_url = os.getenv("GHL_SYSTEM_API_URL", "http://localhost:5001")
        if path_edificio:
            filename_edificio = path_edificio.replace('\\', '/').split('/')[-1]
            foto_edificio = f"{ghl_system_url}/api/cache/files/{filename_edificio}"
            print(f"✅ [CACHE GHL_SYSTEM] Foto Edificio local seleccionada: {foto_edificio}", flush=True)
        if path_montantes:
            filename_montantes = path_montantes.replace('\\', '/').split('/')[-1]
            foto_montantes = f"{ghl_system_url}/api/cache/files/{filename_montantes}"
            print(f"✅ [CACHE GHL_SYSTEM] Foto Montantes local seleccionada: {foto_montantes}", flush=True)

        if not supervisor:
            supervisor = cache_data.get("cf_supervisor_hunting") or cache_data.get("cf_supervisor") or cache_data.get("supervisor") or ""
        if not ejecutivo:
            ejecutivo = cache_data.get("cf_ejecutivo_principal") or cache_data.get("cf_ejecutivo") or cache_data.get("ejecutivo") or ""

    if foto_edificio:
        opp_summary["foto"] = foto_edificio
        opp_summary["foto_edificio"] = foto_edificio
    if foto_montantes:
        opp_summary["foto_montantes"] = foto_montantes

    opp_summary["supervisor"] = supervisor
    opp_summary["ejecutivo"] = ejecutivo

    return opp_summary


def get_pipeline_summary():
    """Obtiene todas las oportunidades del pipeline para el reporte del CEO."""
    url = "https://services.leadconnectorhq.com/opportunities/search"

    params = {
        "location_id": config.LOCATION_ID,
        "pipeline_id": config.PIPELINE_ID,
        "limit": 100
    }

    try:
        response = requests.get(url, headers=HEADERS_GHL, params=params)
        if response.status_code == 200:
            return response.json().get("opportunities", [])
        return []
    except Exception as e:
        print(f"⚠️ Error GHL Summary: {e}")
        return []


def download_image_bytes(url: str) -> bytes:
    """Descarga los bytes de una imagen desde GHL usando autenticación y la comprime para evitar error 413."""
    if not url:
        return None
        
    url = url.strip()
    # Si es un enlace de descarga de documentos de GHL, agregamos el locationId y alt=media
    if "/documents/download/" in url and "locationId=" not in url:
        separador = "&" if "?" in url else "?"
        url = f"{url}{separador}alt=media&locationId={config.LOCATION_ID}"
        
    headers = {}
    if "leadconnectorhq.com" in url or "gohighlevel.com" in url:
        headers = {
            "Authorization": f"Bearer {config.GHL_TOKEN}",
            "Version": "2021-04-15",
            "Accept": "*/*"
        }
    try:
        resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        print(f"📸 [GHL Client] URL: {url}")
        print(f"📸 [GHL Client] Status: {resp.status_code}")

        if resp.status_code == 200:
            raw_bytes = resp.content

            # 🛠️ CONVERTIR Y COMPRIMIR IMAGEN A JPEG (Evita el Error 413 de WhatsApp)
            if PILImage:
                try:
                    img = PILImage.open(io.BytesIO(raw_bytes))
                    img = img.convert("RGB")

                    # 1. Redimensionar de forma más estricta (máximo 800x800, igual que WhatsApp nativo)
                    img.thumbnail((800, 800))

                    out_bytes = io.BytesIO()
                    # 2. Reducir más la calidad para garantizar un payload ligero
                    img.save(out_bytes, format="JPEG", quality=50, optimize=True)

                    final_bytes = out_bytes.getvalue()

                    # Mostrar el peso aproximado en KB en la consola para depurar
                    peso_kb = len(final_bytes) / 1024
                    print(f"📸 [GHL Client] Imagen comprimida con éxito. Peso final: {peso_kb:.2f} KB")

                    return final_bytes
                except Exception as e:
                    print(f"⚠️ Error convirtiendo/comprimiendo imagen: {e}")
            else:
                print("⚠️ [ADVERTENCIA] La librería Pillow no está instalada. Enviando imagen original sin comprimir.")

            return raw_bytes
    except Exception as e:
        print(f"⚠️ Excepción descargando imagen: {e}")
    return None


def consultar_disponibilidad(search_query: str) -> list:
    """Consulta al API de disponibilidad de GHL System pasándole un término de búsqueda."""
    import os
    ghl_system_url = os.getenv("GHL_SYSTEM_API_URL", "http://localhost:5001")
    url = f"{ghl_system_url}/api/disponibilidad"
    try:
        resp = requests.get(url, params={"q": search_query}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        print(f"⚠️ Error consultar_disponibilidad: HTTP {resp.status_code}")
        return []
    except Exception as e:
        print(f"⚠️ Excepción al consultar_disponibilidad: {e}")
        return []