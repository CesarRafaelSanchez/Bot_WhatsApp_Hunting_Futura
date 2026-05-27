from services import ghl_client


def obtener_menu_principal(nombre: str, role: str) -> str:
    """Genera un menú completamente único y aislado según el Rol."""
    role_upper = role.upper()
    if role_upper == "CEO":
        return (
            f"Hola *{nombre}* 👋 (CEO)\n"
            f"Bienvenido al Asistente de Alta Gerencia de Grupo Futura.\n\n"
            f"Por favor, seleccione una opción ejecutiva:\n\n"
            f"*[ 2 ]* Ver reporte estratégico del Pipeline"
        )
    elif role_upper == "HUNTER":
        return (
            f"Hola *{nombre}* 👋\n"
            f"Bienvenido al Panel operativo de Hunters.\n\n"
            f"Por favor, seleccione una opción:\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas en GHL\n"
            f"*[ 4 ]* Histórico de Proyectos ⏳"
        )
    elif role_upper == "BACKOFFICE":
        return (
            f"Hola *{nombre}* 👋 ({role})\n"
            f"Bienvenido al panel de control global.\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas\n"
            f"*[ 2 ]* Ver resumen estratégico del Pipeline"
        )
    else:  # ROL TI
        return (
            f"Hola *{nombre}* 👋 (Administrador TI)\n"
            f"Ecosistema de Automatización de Hunting.\n\n"
            f"Por favor, seleccione una opción:\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas\n"
            f"*[ 2 ]* Ver resumen estratégico del Pipeline\n"
            f"*[ 3 ]* Panel de Administración de Usuarios ⚙️\n"
            f"*[ 4 ]* Histórico de Proyectos (Simular Hunter) ⏳"
        )


def obtener_menu_admin() -> str:
    """Submenú exclusivo para gestión de altas, bajas y cambios de rol."""
    return (
        "⚙️ *Panel de Control de Usuarios (Solo TI)*\n\n"
        "Seleccione la acción que desea ejecutar:\n\n"
        "*[ 31 ]* Registrar nuevo usuario (Alta)\n"
        "*[ 32 ]* Dar de baja a un usuario (Baja)\n"
        "*[ 33 ]* Modificar Rol de un usuario\n\n"
        "*[ 0 ]* Volver al Menú Principal"
    )


def obtener_menu_historico() -> str:
    """Submenú secundario para segmentar el tipo de histórico (UX Campo/Oficina)."""
    return (
        "⏳ *Histórico de Proyectos (Límite: Últimos 20)*\n\n"
        "Seleccione cómo desea consultar su información:\n\n"
        "*[ 41 ]* Ver proyectos por Estado (Ganados / Perdidos)\n"
        "*[ 42 ]* Ver histórico General (Cronológico)\n"
        "*[ 43 ]* Buscar un proyecto por su Nombre 🔍\n\n"
        "*[ 0 ]* Volver al Menú Principal"
    )


def obtener_menu_filtro_estados() -> str:
    """Submenú para elegir entre proyectos ganados o perdidos."""
    return (
        "🎭 *Filtrar Histórico por Estado*\n\n"
        "*[ 411 ]* Ver Habilitaciones Completas (Ganados)\n"
        "*[ 412 ]* Ver Hunting Perdidos / No Recuperables\n\n"
        "*[ 4 ]* Volver al Menú de Historial"
    )


def formatear_lista_historico(opportunities) -> str:
    """Helper genérico para dibujar la ficha completa en WhatsApp."""
    if not opportunities:
        return "📋 *Estatus de Oportunidades:*\n\nNo se encontraron registros que coincidan con los criterios."

    reply = f"📋 *Registros Encontrados ({len(opportunities)})*\n"
    reply += "Alineado con el pipeline real de Hunting.\n"
    reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"

    for idx, opp in enumerate(opportunities, 1):
        reply += f"*{idx}. {opp['name']}*\n"
        reply += f"🏢 *Inmobiliaria:* {opp['inmobiliaria']}\n"
        reply += f"📍 *Dirección:* {opp['direccion']}\n"
        if opp['foto']:
            reply += f"📸 *Foto del Edificio:* {opp['foto']}\n"
        reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    return reply


def procesar_opcion_hunter(ghl_id: str) -> str:
    """Mapea directamente a la lista unificada con formato completo (Opción 1)."""
    opportunities = ghl_client.get_opportunities_by_user(ghl_id)
    return formatear_lista_historico(opportunities)


def procesar_opcion_ceo() -> str:
    """Consolida las etapas para el reporte del CEO."""
    opportunities = ghl_client.get_pipeline_summary()
    if not opportunities:
        return "No se encontraron oportunidades en el Pipeline de Hunting."

    fase_prospeccion = 0
    fase_win = 0
    fase_tecnica = 0
    fase_completado = 0
    fase_perdido = 0
    otras_etapas = 0

    STAGES_PROSPECCION = ["4d5d6906-d70f-466a-9b9b-0acf0a203138", "d8481911-0c96-4a53-a246-3f43170a6d24"]
    STAGE_WIN = "fdc27149-b398-4ed7-9271-946c66dc9f0f"
    STAGES_TECNICA = ["46400c15-10a3-4c96-a5b0-76f0cf65b753", "5214c97a-30b6-44b4-8f6f-dd1798622a8b"]
    STAGE_COMPLETADO = "dc5a218f-50a8-4bb6-9351-82b2f10d9886"
    STAGE_PERDIDO = "b9549f80-9858-4e84-8afc-aacdcd4db23f"

    for opp in opportunities:
        stage_id = opp.get("pipelineStageId")
        if stage_id in STAGES_PROSPECCION:
            fase_prospeccion += 1
        elif stage_id == STAGE_WIN:
            fase_win += 1
        elif stage_id in STAGES_TECNICA:
            fase_tecnica += 1
        elif stage_id == STAGE_COMPLETADO:
            fase_completado += 1
        elif stage_id == STAGE_PERDIDO:
            fase_perdido += 1
        else:
            otras_etapas += 1

    reply = f"📊 *Resumen Ejecutivo: Hunting & Habilitación* 🚀\n\n"
    reply += f"• *Total Proyectos en Pipeline:* {len(opportunities)}\n\n"
    reply += f"🎯 *Fase 1 (Prospección Inicial):* {fase_prospeccion}\n"
    reply += f"⏳ *Fase 2 (Esperando Respuesta WIN):* {fase_win} ⚠️\n"
    reply += f"🏗️ *Fase 3 (En Habilitación Técnica):* {fase_tecnica}\n"
    reply += f"✅ *Fase 4 (Habilitación Completa):* {fase_completado}\n"
    reply += f"❌ *Fase 5 (Hunting Perdidos):* {fase_perdido}\n"

    if otras_etapas > 0:
        reply += f"📁 *Otras etapas en proceso:* {otras_etapas}\n"

    reply += f"\n💡 _Datos reales extraídos en vivo desde GoHighLevel._"
    return reply