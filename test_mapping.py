from services.ghl_client import _get_contact_details, _extract_project_fields, _build_opportunity_summary

contact = _get_contact_details('K1F0eWeO1DUiLARx2swX')
fields = _extract_project_fields(contact)

print('Campos extraídos:')
for k, v in fields.items():
    print(f'  {k}: {v}')

opp = {
    'name': 'SANTA CLARA FIX CESAR',
    'pipelineStageId': 'dc5a218f-50a8-4bb6-9351-82b2f10d9886',
    'contactId': 'K1F0eWeO1DUiLARx2swX',
    'contact': contact
}

summary = _build_opportunity_summary(opp)
print('\nResumen de oportunidad:')
print(f'  nombre: {summary["name"]}')
print(f'  inmobiliaria: {summary["inmobiliaria"]}')
print(f'  direccion: {summary["direccion"]}')
print(f'  coordenadas: {summary["coordenadas"]}')
