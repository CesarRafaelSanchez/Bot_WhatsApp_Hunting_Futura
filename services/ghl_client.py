import requests
import config

HEADERS_GHL = {
    "Authorization": f"Bearer {config.GHL_TOKEN}",
    "Version": "2021-04-15",
    "Content-Type": "application/json"
}


def get_opportunities_by_user(ghl_user_id: str):
    """Obtiene y formatea las oportunidades operativas activas para el Hunter (Opción 1 - Límite 100)."""
    url = "https://services.leadconnectorhq.com/opportunities/search"

    params = {
        "location_id": config.LOCATION_ID,
        "pipeline_id": config.PIPELINE_ID,
        "assigned_to": ghl_user_id,
        "limit": 100
    }

    try:
        response = requests.get(url, headers=HEADERS_GHL, params=params)
        if response.status_code != 200:
            return []

        opps = response.json().get("opportunities", [])
        formatted_list = []

        for opp in opps:
            contact = opp.get("contact", {})
            direccion = contact.get("address", "No especificada") or "No especificada"
            inmobiliaria = "No especificada"
            foto_url = None

            # Consolidamos todos los posibles campos personalizados del contacto y la oportunidad
            custom_fields = contact.get("customFields", []) + opp.get("customFields", [])
            for field in custom_fields:
                f_id = str(field.get("id", "")).lower()
                f_key = str(field.get("key", "")).lower()
                f_value = field.get("value", "")

                if not f_value:
                    continue

                # Validación robusta por texto clave en ID o KEY
                if "inmobiliaria" in f_key or "constructora" in f_key or "inmobiliaria" in f_id:
                    inmobiliaria = str(f_value)
                elif "foto" in f_key or "imagen" in f_key or "foto" in f_id:
                    foto_url = str(f_value)
                elif "direccion" in f_key or "dirección" in f_key or "direccion" in f_id:
                    direccion = str(f_value)

            formatted_list.append({
                "name": opp.get("name", "Sin Nombre").upper(),
                "direccion": direccion,
                "inmobiliaria": inmobiliaria,
                "foto": foto_url,
                "stage": opp.get("pipelineStageId", "En proceso")
            })

        return formatted_list
    except Exception as e:
        print(f"⚠️ Error GHL Hunter Extractor: {e}")
        return []


def get_opportunities_advanced(ghl_user_id: str, search_query: str = None, stage_id: str = None):
    """Consulta avanzada en GHL v2 filtrando por query o etapa específica (Opción 4 - Límite 20)."""
    url = "https://services.leadconnectorhq.com/opportunities/search"

    params = {
        "location_id": config.LOCATION_ID,
        "pipeline_id": config.PIPELINE_ID,
        "assigned_to": ghl_user_id,
        "limit": 20
    }

    if search_query:
        params["q"] = search_query

    if stage_id:
        params["pipeline_stage_id"] = stage_id

    try:
        response = requests.get(url, headers=HEADERS_GHL, params=params)
        if response.status_code != 200:
            return []

        opps = response.json().get("opportunities", [])
        formatted_list = []

        for opp in opps:
            contact = opp.get("contact", {})
            direccion = contact.get("address", "No especificada") or "No especificada"
            inmobiliaria = "No especificada"
            foto_url = None

            custom_fields = contact.get("customFields", []) + opp.get("customFields", [])
            for field in custom_fields:
                f_id = str(field.get("id", "")).lower()
                f_key = str(field.get("key", "")).lower()
                f_value = field.get("value", "")

                if not f_value:
                    continue

                if "inmobiliaria" in f_key or "constructora" in f_key or "inmobiliaria" in f_id:
                    inmobiliaria = str(f_value)
                elif "foto" in f_key or "imagen" in f_key or "foto" in f_id:
                    foto_url = str(f_value)
                elif "direccion" in f_key or "dirección" in f_key or "direccion" in f_id:
                    direccion = str(f_value)

            formatted_list.append({
                "name": opp.get("name", "Sin Nombre").upper(),
                "direccion": direccion,
                "inmobiliaria": inmobiliaria,
                "foto": foto_url,
                "stage": opp.get("pipelineStageId", "En proceso")
            })

        return formatted_list
    except Exception as e:
        print(f"⚠️ Error GHL Advanced Extractor: {e}")
        return []


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