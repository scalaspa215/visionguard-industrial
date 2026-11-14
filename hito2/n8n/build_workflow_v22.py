"""
VisionGuard Industrial - construye el workflow v2.2 a partir del respaldo v2.1.

No edita el original: lee  ../../original/workflow_backup_original.json
y escribe:
  VisionGuard_v2.2_Hito2_IMPORTAR.json  -> para importar en TU n8n (conserva
                                           referencias a credenciales, correo y chat)
  VisionGuard_v2.2_Hito2_PUBLICO.json   -> anonimizado para GitHub/entrega
  VisionGuard_v2.2_Error_Handler_PUBLICO.json -> workflow de errores (Error Trigger)
Uso: python build_workflow_v22.py
"""
import copy
import json
import re
import uuid
from pathlib import Path

AQUI = Path(__file__).parent
ORIGEN = AQUI.parents[1] / "original" / "workflow_backup_original.json"
NODOS_PY = AQUI.parent / "python" / "n8n_nodes"

w = json.loads(ORIGEN.read_text(encoding="utf-8"))
N = {n["name"]: n for n in w["nodes"]}
C = w["connections"]

SHEET_ID = N["Lectura_NLP"]["parameters"]["documentId"]["value"]   # se lee del respaldo, no se publica
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
EMAIL = N["Notificacion_Analisis_Integrado"]["parameters"]["sendTo"]
CHAT = N["Notificacion_Telegram_Integrado"]["parameters"]["chatId"]
CRED_GMAIL = N["Notificacion_Analisis_Integrado"]["credentials"]
CRED_TG = N["Notificacion_Telegram_Integrado"]["credentials"]
CRED_SHEETS = N["Lectura_NLP"]["credentials"]
CRED_DRIVE = N["Move file"]["credentials"]


def uid():
    return str(uuid.uuid4())


def nodo(name, type_, ver, pos, params, **extra):
    n = {"parameters": params, "type": type_, "typeVersion": ver, "position": pos, "id": uid(), "name": name}
    n.update(extra)
    w["nodes"].append(n)
    N[name] = n
    return n


def conectar(src, dst, out=0, inp=0):
    salidas = C.setdefault(src, {}).setdefault("main", [])
    while len(salidas) <= out:
        salidas.append([])
    salidas[out].append({"node": dst, "type": "main", "index": inp})


def desconectar(src, dst):
    for salida in C.get(src, {}).get("main", []):
        salida[:] = [c for c in salida if c["node"] != dst]


def leer_codigo(nombre):
    return (NODOS_PY / nombre).read_text(encoding="utf-8")


CFG = "$('Config').first().json"

# ------------------------------------------------------------------ 1. Config
nodo("Config", "n8n-nodes-base.set", 3.4, [-416, 400], {
    "assignments": {"assignments": [
        {"id": uid(), "name": "dashboard_url", "value": SHEET_URL + "#gid=0", "type": "string"},
        {"id": uid(), "name": "historial_url", "value": SHEET_URL, "type": "string"},
        {"id": uid(), "name": "email_responsable", "value": EMAIL, "type": "string"},
        {"id": uid(), "name": "telegram_chat_id", "value": CHAT, "type": "string"},
        {"id": uid(), "name": "umbral_confianza", "value": 0.9, "type": "number"},
        {"id": uid(), "name": "umbral_pronostico_pct", "value": 7.5, "type": "number"},
        {"id": uid(), "name": "umbral_discrepancia_pp", "value": 1.5, "type": "number"},
        {"id": uid(), "name": "version", "value": "VisionGuard v2.2 - Hito 2", "type": "string"},
    ]},
    "options": {},
})
# Disparador: los tres turnos (07:00, 15:00, 23:00) en vez de solo 08:00.
N["Schedule Trigger"]["parameters"] = {"rule": {"interval": [
    {"triggerAtHour": 7}, {"triggerAtHour": 15}, {"triggerAtHour": 23}]}}
destinos_trigger = [c["node"] for c in C["Schedule Trigger"]["main"][0]]
C["Schedule Trigger"]["main"] = [[{"node": "Config", "type": "main", "index": 0}]]
for d in destinos_trigger:
    conectar("Config", d)

# ------------------------------------------------- 2. Rama legado Hito 1 apagada
# HTTP Request -> Message a model llamaba a GPT por imagen y terminaba en nodos
# deshabilitados: gasto sin efecto. Se desconecta y se deshabilita (no se borra).
desconectar("HTTP Request", "Message a model")
for nombre in ["Message a model", "Code in JavaScript"]:
    N[nombre]["disabled"] = True
    N[nombre]["notes"] = "LEGADO HITO 1 - reemplazado por LLM_Integrado + Validacion_Seguridad_Final"
    N[nombre]["notesInFlow"] = True

# La inferencia ResNet18 no debe botar todo el flujo por una imagen corrupta.
N["HTTP Request"].update({"onError": "continueRegularOutput", "retryOnFail": True,
                          "maxTries": 3, "waitBetweenTries": 3000})
N["HTTP Request"]["parameters"]["options"] = {"timeout": 120000}

# ------------------------------------------------ 3. API caida: alerta activa
N["Send a message1"].pop("disabled", None)
N["Send a message1"]["parameters"]["sendTo"] = "={{ " + CFG + ".email_responsable }}"
N["Send a message1"]["parameters"]["message"] = (
    N["Send a message1"]["parameters"]["message"].replace(
        "<hr>", "<p><b>Panel:</b> <a href=\"{{ " + CFG + ".dashboard_url }}\">VisionGuard Dashboard</a></p><hr>"))
N["Send a message1"]["parameters"]["message"] = "=" + N["Send a message1"]["parameters"]["message"].lstrip("=")
N["Send a message1"]["retryOnFail"] = True
nodo("Telegram_API_Caida", "n8n-nodes-base.telegram", 1.2, [1088, 336], {
    "chatId": "={{ " + CFG + ".telegram_chat_id }}",
    "text": "={{ '🚨 VISIONGUARD | API ResNet18 NO DISPONIBLE\\nDos verificaciones /health fallaron (60 s de espera).\\n"
            "No se procesaron inspecciones en este turno.\\nPanel: ' + " + CFG + ".dashboard_url }}",
    "additionalFields": {"appendAttribution": False}},
    credentials=CRED_TG, retryOnFail=True, onError="continueRegularOutput")
conectar("If2", "Telegram_API_Caida", out=1)

# ------------------------------------------- 4. Carpeta sin imagenes pendientes
N["Search files and folders1"]["alwaysOutputData"] = True
desconectar("Search files and folders1", "Download file")
nodo("Hay_Imagenes_Pendientes", "n8n-nodes-base.if", 2.2, [1232, 0], {
    "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                   "conditions": [{"id": uid(), "leftValue": "={{ !!$json.id }}", "rightValue": "",
                                   "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                   "combinator": "and"},
    "options": {}})
conectar("Search files and folders1", "Hay_Imagenes_Pendientes")
conectar("Hay_Imagenes_Pendientes", "Download file", out=0)
N["Download file"]["position"] = [1408, -96]
N["HTTP Request"]["position"] = [1600, -96]

MSG_SIN = ("={{ `<h2>VisionGuard Industrial | Turno sin inspecciones pendientes</h2>"
           "<p>No se encontraron imagenes nuevas en <b>Inspecciones_Pendientes</b> en esta ejecucion "
           "(${$now.setZone('America/Santiago').toFormat('yyyy-MM-dd HH:mm')}).</p>"
           "<p>Los modelos GRU y NLP siguen registrandose en el historial.</p>"
           "<p><a href=\"${" + CFG + ".dashboard_url}\">Abrir panel VisionGuard</a></p>"
           "<hr><p><small>Prototipo academico. Ninguna pieza se aprueba automaticamente.</small></p>` }}")
nodo("Aviso_Sin_Pendientes_Gmail", "n8n-nodes-base.gmail", 2.2, [1440, 112], {
    "sendTo": "={{ " + CFG + ".email_responsable }}",
    "subject": "VisionGuard | Sin inspecciones pendientes en este turno",
    "message": MSG_SIN, "options": {"appendAttribution": False}},
    credentials=CRED_GMAIL, retryOnFail=True, onError="continueRegularOutput")
nodo("Aviso_Sin_Pendientes_Telegram", "n8n-nodes-base.telegram", 1.2, [1440, 256], {
    "chatId": "={{ " + CFG + ".telegram_chat_id }}",
    "text": "={{ 'ℹ️ VISIONGUARD | Sin imagenes pendientes en este turno.\\nPanel: ' + " + CFG + ".dashboard_url }}",
    "additionalFields": {"appendAttribution": False}},
    credentials=CRED_TG, retryOnFail=True, onError="continueRegularOutput")
conectar("Hay_Imagenes_Pendientes", "Aviso_Sin_Pendientes_Gmail", out=1)
conectar("Hay_Imagenes_Pendientes", "Aviso_Sin_Pendientes_Telegram", out=1)

# ------------------------------------------------ 5. Historial GRU activado
g = N["Append or update row in sheet"]
g.pop("disabled", None)
g["onError"] = "continueRegularOutput"
g["parameters"]["columns"]["value"]["clave_unica"] = (
    "={{ $now.setZone('America/Santiago').toFormat('yyyy-MM-dd') + '|' + String($json.linea).trim() }}")
g["parameters"]["columns"]["value"]["fecha_registro"] = (
    "={{ $now.setZone('America/Santiago').toFormat('yyyy-MM-dd HH:mm:ss') }}")
N["HTTP Request4"]["onError"] = "continueRegularOutput"
N["HTTP Request3"].update({"maxTries": 4, "waitBetweenTries": 5000})

# ---------------------------------------------- 6. Transformer NLP en vivo
nodo("Leer_Reportes_NC", "n8n-nodes-base.googleSheets", 4.7, [-64, 1056], {
    "documentId": copy.deepcopy(N["Lectura_NLP"]["parameters"]["documentId"]),
    "sheetName": {"__rl": True, "value": "Reportes_NC", "mode": "name"},
    "options": {}},
    credentials=CRED_SHEETS, onError="continueRegularOutput", alwaysOutputData=True)
nodo("Preparar_Textos_NLP", "n8n-nodes-base.code", 2, [144, 1056],
     {"jsCode": leer_codigo("preparar_textos_nlp.js")})
nodo("Embeddings_Transformer_HF", "n8n-nodes-base.httpRequest", 4.2, [352, 1152], {
    "method": "POST",
    "url": "https://router.huggingface.co/hf-inference/models/sentence-transformers/"
           "paraphrase-multilingual-MiniLM-L12-v2/pipeline/feature-extraction",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendBody": True, "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify($json.cuerpo_hf) }}",
    "options": {"timeout": 120000,
                "response": {"response": {"responseFormat": "text", "outputPropertyName": "respuesta_hf"}}}},
    retryOnFail=True, maxTries=3, waitBetweenTries=5000, onError="continueRegularOutput",
    notes="Credencial Header Auth: Name=Authorization, Value=Bearer <token HF de solo lectura>",
    notesInFlow=True)
nodo("Unir_Textos_Embeddings", "n8n-nodes-base.merge", 3.2, [560, 1056],
     {"mode": "combine", "combineBy": "combineByPosition", "options": {}})
nodo("Parsear_Embeddings", "n8n-nodes-base.code", 2, [752, 1056],
     {"jsCode": leer_codigo("parsear_embeddings.js")})
nodo("Clasificar_NLP_Python", "n8n-nodes-base.code", 2, [944, 1056],
     {"language": "pythonNative", "pythonCode": leer_codigo("clasificar_nlp.py")},
     notes="Python (nativo). Si tu instancia no tiene Python, habilita Clasificar_NLP_JS_respaldo y deshabilita este.",
     notesInFlow=True)
nodo("Clasificar_NLP_JS_respaldo", "n8n-nodes-base.code", 2, [944, 1248],
     {"jsCode": leer_codigo("clasificar_nlp_respaldo.js")}, disabled=True)
conectar("Config", "Leer_Reportes_NC")
conectar("Leer_Reportes_NC", "Preparar_Textos_NLP")
conectar("Preparar_Textos_NLP", "Embeddings_Transformer_HF")
conectar("Preparar_Textos_NLP", "Unir_Textos_Embeddings", inp=0)
conectar("Embeddings_Transformer_HF", "Unir_Textos_Embeddings", inp=1)
conectar("Unir_Textos_Embeddings", "Parsear_Embeddings")
conectar("Parsear_Embeddings", "Clasificar_NLP_Python")
N["Merge"]["parameters"]["numberInputs"] = 4
conectar("Clasificar_NLP_Python", "Merge", inp=3)
N["Lectura_NLP"]["onError"] = "continueRegularOutput"
N["Lectura_NLP"]["alwaysOutputData"] = True

# ----------------------------------------------- 7. Integracion + LLM + control
N["Integracion_3_Modelos"]["parameters"]["jsCode"] = leer_codigo("integracion_3_modelos.js")
llm = N["LLM_Integrado"]
llm.update({"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000, "onError": "continueRegularOutput"})
prompt = llm["parameters"]["responses"]["values"][0]["content"]
REEMPLAZOS = [
    ("Los resultados NLP proceden de registros previamente almacenados. No se ha verificado una nueva "
     "inferencia directa del Transformer en esta ejecución.",
     "El componente NLP clasifica en esta ejecución reportes de no conformidad SIMULADOS con un Transformer "
     "de embeddings (paraphrase-multilingual-MiniLM-L12-v2) y con reglas fijas. El campo "
     "nlp_transformer.transformer_ejecutado indica si la inferencia del Transformer se completó; si es false, "
     "solo existe la clasificación por reglas."),
    ("17. No afirmes que se ejecutó nuevamente el Transformer si no existe evidencia de ello.",
     "17. Afirma que el Transformer se ejecutó solo si nlp_transformer.transformer_ejecutado es true. Reporta "
     "sus métricas de prueba frente a las reglas tal como vienen, sin exagerarlas, y la causa principal de los "
     "reportes de operación."),
    ("REGLAS DE SEGURIDAD INDUSTRIAL:",
     "REGLAS DE ALERTAS Y VERIFICACIÓN:\n\n19b. Menciona explícitamente cada elemento de la lista \"alertas\" "
     "y su implicancia.\n\n19c. Todo número que escribas debe aparecer en DATOS RECIBIDOS: un control "
     "automático posterior compara cada cifra de tu respuesta con los datos y marca las no respaldadas.\n\n"
     "REGLAS DE SEGURIDAD INDUSTRIAL:"),
]
for viejo, nuevo in REEMPLAZOS:
    assert viejo in prompt, f"No se encontro en el prompt: {viejo[:60]}"
    prompt = prompt.replace(viejo, nuevo)
llm["parameters"]["responses"]["values"][0]["content"] = prompt
N["Validacion_Seguridad_Final"]["parameters"]["jsCode"] = leer_codigo("validacion_seguridad_final.js")
N["Preparar_Registro_Integrado"]["parameters"]["jsCode"] = leer_codigo("preparar_registro_integrado.js")

# ------------------------- 8. Dedupe ANTES de guardar (no pisar decisiones humanas)
desconectar("Preparar_Registro_Integrado", "Guardar_Analisis_Integrado")
desconectar("Guardar_Analisis_Integrado", "Evitar_Notificaciones_Duplicadas")
for d in ["Notificacion_Analisis_Integrado", "Notificacion_Telegram_Integrado", "Aprobacion_Humana_Integrada"]:
    desconectar("Evitar_Notificaciones_Duplicadas", d)
conectar("Preparar_Registro_Integrado", "Evitar_Notificaciones_Duplicadas")
conectar("Evitar_Notificaciones_Duplicadas", "Guardar_Analisis_Integrado")
N["Evitar_Notificaciones_Duplicadas"]["position"] = [2208, 672]
N["Guardar_Analisis_Integrado"]["position"] = [2384, 672]
N["Guardar_Analisis_Integrado"].update({"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000})
N["Guardar_Analisis_Integrado"]["parameters"]["options"] = {"handlingExtraData": "insertInNewColumn"}

# ----------------------------------- 9. Bucle por inspeccion (1 aprobacion c/u)
nodo("Loop_Inspecciones", "n8n-nodes-base.splitInBatches", 3, [2560, 672], {"batchSize": 1, "options": {}})
conectar("Guardar_Analisis_Integrado", "Loop_Inspecciones")
# salida 1 = "loop" (salida 0 = "done")
for d in ["Notificacion_Analisis_Integrado", "Notificacion_Telegram_Integrado", "Aprobacion_Humana_Integrada"]:
    conectar("Loop_Inspecciones", d, out=1)
N["Notificacion_Analisis_Integrado"]["position"] = [2800, 400]
N["Notificacion_Telegram_Integrado"]["position"] = [2800, 576]
N["Aprobacion_Humana_Integrada"]["position"] = [2800, 864]

ESC = "const e = s => String(s ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));"
PCT = "const pct = v => Number.isFinite(Number(v)) ? (Number(v) * 100).toFixed(2) + ' %' : 'n/d';"
gm = N["Notificacion_Analisis_Integrado"]
gm["parameters"]["sendTo"] = "={{ " + CFG + ".email_responsable }}"
gm["parameters"]["subject"] = (
    "={{ ($json.tiene_alertas ? '🚨 ' : '') + 'VisionGuard | ' + $json.clasificacion + ' | Prioridad ' "
    "+ String($json.prioridad).toUpperCase() + ' | ' + $json.archivo }}")
gm["parameters"]["message"] = "={{ (() => { " + ESC + PCT + " const c = " + CFG + "; const d = $json; return `" + """
<div style="font-family:Arial,sans-serif;max-width:680px;color:#17283f">
<h2 style="margin:0 0 4px">VisionGuard Industrial · Informe de inspección integrada</h2>
<p style="margin:0 0 14px;color:#5d6f89">${e(d.fecha_registro)} · ${e(c.version)}</p>
<table style="border-collapse:collapse;width:100%;font-size:14px">
<tr><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>Archivo</b></td><td style="padding:6px;border-bottom:1px solid #dce5f1">${e(d.archivo)}</td></tr>
<tr><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>ResNet18</b></td><td style="padding:6px;border-bottom:1px solid #dce5f1">${e(d.clasificacion)} · confianza ${pct(d.confianza)}</td></tr>
<tr><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>Prioridad</b></td><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>${e(String(d.prioridad).toUpperCase())}</b></td></tr>
<tr><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>GRU (simulado)</b></td><td style="padding:6px;border-bottom:1px solid #dce5f1">Línea ${e(d.linea_mayor_pronostico)} · ${e(d.pronostico_max_pct)} % de defectos pronosticado</td></tr>
<tr><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>NLP Transformer</b></td><td style="padding:6px;border-bottom:1px solid #dce5f1">Causa principal NC: ${e(d.nlp_causa_principal)} (${d.nlp_transformer_ejecutado ? 'Transformer ejecutado' : 'solo reglas'})</td></tr>
<tr><td style="padding:6px;border-bottom:1px solid #dce5f1"><b>Fuente del análisis</b></td><td style="padding:6px;border-bottom:1px solid #dce5f1">${e(d.fuente_analisis)}${d.alucinacion_sospechada ? ' · ⚠️ cifras no respaldadas detectadas' : ''}</td></tr>
<tr><td style="padding:6px"><b>Estado</b></td><td style="padding:6px">${e(d.estado)}</td></tr>
</table>
${d.tiene_alertas ? `<p style="background:#fff2f1;color:#9a2f27;padding:10px;border-radius:8px"><b>Alertas:</b> ${e(d.alertas)}</p>` : ''}
<h3>Diagnóstico (IA)</h3><p>${e(d.diagnostico)}</p>
<h3>Recomendación</h3><p>${e(d.recomendacion)}</p>
<p><b>Requiere revisión humana:</b> Sí · <b>Aprobación automática:</b> No</p>
<p style="margin:18px 0"><a href="${e(c.dashboard_url)}" style="background:#3557bd;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none">📊 Abrir panel interactivo</a></p>
<p style="font-size:12px;color:#61738b">Panel: indicadores, resultados de ResNet18, GRU y NLP en el tiempo e historial de recomendaciones. Historial: <a href="${e(c.historial_url)}">Google Sheets</a>.</p>
<hr><p style="font-size:12px;color:#61738b">Prototipo académico. Datos GRU y NLP simulados. Recibirá un correo aparte para APROBAR o RECHAZAR la acción.</p>
</div>`; })() }}"""
gm["parameters"]["options"] = {"appendAttribution": False}
gm.update({"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000, "onError": "continueRegularOutput"})

tg = N["Notificacion_Telegram_Integrado"]
tg["parameters"]["chatId"] = "={{ " + CFG + ".telegram_chat_id }}"
tg["parameters"]["text"] = "={{ (() => { " + PCT + " const c = " + CFG + "; const d = $json; const corto = (s, n) => { s = String(s ?? ''); return s.length > n ? s.slice(0, n) + '…' : s; }; return `" + """🛡️ VISIONGUARD · INSPECCIÓN ${d.tiene_alertas ? '🚨' : ''}
📁 ${d.archivo}
🔍 ResNet18: ${d.clasificacion} (${pct(d.confianza)})
🚦 Prioridad: ${String(d.prioridad).toUpperCase()}
📈 GRU simulado: ${d.linea_mayor_pronostico} → ${d.pronostico_max_pct} %
📝 NLP: causa principal ${d.nlp_causa_principal}${d.nlp_transformer_ejecutado ? '' : ' (solo reglas)'}
${d.tiene_alertas ? '⚠️ ' + corto(d.alertas, 300) + '\\n' : ''}
🤖 ${corto(d.diagnostico, 600)}

✅ ${corto(d.recomendacion, 400)}

👤 Revisión humana obligatoria. Responda el correo de aprobación.
📊 Panel: ${c.dashboard_url}`; })() }}"""
tg["parameters"]["additionalFields"] = {"appendAttribution": False}
tg.update({"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000, "onError": "continueRegularOutput"})

nodo("Mover_A_Procesadas", "n8n-nodes-base.googleDrive", 3, [3024, 400], {
    "operation": "move",
    "fileId": {"__rl": True, "mode": "id",
               "value": "={{ $('Search files and folders1').all().find(i => i.json.name === $('Loop_Inspecciones').first().json.archivo)?.json.id }}"},
    "driveId": copy.deepcopy(N["Move file"]["parameters"]["driveId"]),
    "folderId": copy.deepcopy(N["Move file"]["parameters"]["folderId"])},
    credentials=CRED_DRIVE, onError="continueRegularOutput")
conectar("Notificacion_Analisis_Integrado", "Mover_A_Procesadas")

ap = N["Aprobacion_Humana_Integrada"]
ap["parameters"]["sendTo"] = "={{ " + CFG + ".email_responsable }}"
ap["parameters"]["subject"] = "={{ 'VisionGuard | Validación humana requerida | ' + $json.archivo + ' | ' + $json.clasificacion }}"
ap["parameters"]["message"] = ap["parameters"]["message"].replace(
    "VisionGuard Industrial | Prototipo académico.",
    "Panel interactivo: ${" + CFG + ".dashboard_url}\n\nVisionGuard Industrial | Prototipo académico. "
    "Si no responde en 8 horas la inspección queda como SIN_RESPUESTA_HUMANA_ESCALAR.")
ap["parameters"]["options"] = {"limitWaitTime": {"values": {
    "limitType": "afterTimeInterval", "resumeAmount": 8, "resumeUnit": "hours"}}}

vr = N["Validar_Respuesta_Humana"]["parameters"]["conditions"]
vr["options"]["typeValidation"] = "loose"
vr["conditions"][0]["leftValue"] = "={{ $json.data?.approved === true }}"

AHORA = "={{ $now.setZone('America/Santiago').toFormat('yyyy-MM-dd HH:mm:ss') }}"
CLAVE = "={{ $('Loop_Inspecciones').first().json.clave_unica }}"
ARCH = "={{ $('Loop_Inspecciones').first().json.archivo }}"


def set_asig(nombre, campos):
    N[nombre]["parameters"]["assignments"]["assignments"] = [
        {"id": uid(), "name": k, "value": v, "type": t} for k, v, t in campos]


set_asig("Preparar_Aprobacion_Humana", [
    ("clave_unica", CLAVE, "string"), ("archivo", ARCH, "string"),
    ("validacion_humana_realizada", True, "boolean"),
    ("estado", "ACCION_AUTORIZADA_POR_HUMANO", "string"),
    ("decision_humana", "APROBAR", "string"), ("fecha_decision_humana", AHORA, "string")])
set_asig("Preparar_Rechazo_Humano", [
    ("clave_unica", CLAVE, "string"), ("archivo", ARCH, "string"),
    ("validacion_humana_realizada", "={{ $json.data?.approved === false }}", "boolean"),
    ("estado", "={{ $json.data?.approved === false ? 'ACCION_RECHAZADA_POR_HUMANO' : 'SIN_RESPUESTA_HUMANA_ESCALAR' }}", "string"),
    ("decision_humana", "={{ $json.data?.approved === false ? 'RECHAZAR' : 'SIN_RESPUESTA' }}", "string"),
    ("fecha_decision_humana", AHORA, "string")])

rd = N["Registrar_Decision_Humana"]
rd["parameters"]["columns"]["value"] = {"clave_unica": "={{ $json.clave_unica }}"}
rd["parameters"]["options"] = {"handlingExtraData": "insertInNewColumn"}
rd.update({"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000})

fin = N["Send a message2"]
fin["parameters"]["sendTo"] = "={{ " + CFG + ".email_responsable }}"
fin["parameters"]["subject"] = "={{ 'VisionGuard | Decisión humana: ' + $('Preparar_Registro_Final').first().json.decision_humana + ' | ' + $('Preparar_Registro_Final').first().json.archivo }}"
fin["parameters"]["message"] = "={{ (() => { " + ESC + " const c = " + CFG + "; const d = $('Preparar_Registro_Final').first().json; return `" + """
<h2>VisionGuard | Decisión humana registrada</h2>
<p><b>Archivo:</b> ${e(d.archivo)}<br><b>Inspección:</b> ${e(d.clave_unica)}</p>
<p><b>Decisión:</b> ${e(d.decision_humana)} → <b>${e(d.estado)}</b><br><b>Fecha:</b> ${e(d.fecha_decision_humana)}</p>
<p>${d.decision_humana === 'SIN_RESPUESTA' ? '⚠️ No hubo respuesta en el plazo: escalar al jefe de calidad. La pieza permanece apartada.' : 'La decisión quedó registrada en Google Sheets (Analisis_Integrado).'}</p>
<p>Autorizar la acción NO certifica que la pieza esté libre de defectos.</p>
<p><a href="${e(c.dashboard_url)}">📊 Abrir panel VisionGuard</a></p>`; })() }}"""
fin["parameters"]["options"] = {"appendAttribution": False}
fin.update({"retryOnFail": True, "onError": "continueRegularOutput"})

# Nodo pasarela para conservar los datos de la decision despues de Sheets
nodo("Preparar_Registro_Final", "n8n-nodes-base.noOp", 1, [3104, 880], {})
desconectar("Preparar_Aprobacion_Humana", "Registrar_Decision_Humana")
desconectar("Preparar_Rechazo_Humano", "Registrar_Decision_Humana")
conectar("Preparar_Aprobacion_Humana", "Preparar_Registro_Final")
conectar("Preparar_Rechazo_Humano", "Preparar_Registro_Final")
desconectar("Registrar_Decision_Humana", "Send a message2")
conectar("Preparar_Registro_Final", "Registrar_Decision_Humana")
conectar("Registrar_Decision_Humana", "Send a message2")
N["Registrar_Decision_Humana"]["position"] = [3296, 880]
N["Send a message2"]["position"] = [3488, 880]

nodo("Notificacion_Final_Telegram", "n8n-nodes-base.telegram", 1.2, [3680, 880], {
    "chatId": "={{ " + CFG + ".telegram_chat_id }}",
    "text": "={{ (() => { const d = $('Preparar_Registro_Final').first().json; const icono = d.decision_humana === 'APROBAR' ? '✅' : (d.decision_humana === 'RECHAZAR' ? '⛔' : '⏰'); "
            "return `${icono} VISIONGUARD · DECISIÓN HUMANA\\n📁 ${d.archivo}\\n👤 ${d.decision_humana} → ${d.estado}\\n🕒 ${d.fecha_decision_humana}\\n"
            "📊 Panel: ${" + CFG + ".dashboard_url}`; })() }}",
    "additionalFields": {"appendAttribution": False}},
    credentials=CRED_TG, retryOnFail=True, onError="continueRegularOutput")
conectar("Send a message2", "Notificacion_Final_Telegram")
conectar("Notificacion_Final_Telegram", "Loop_Inspecciones")   # siguiente inspeccion

# ----------------------------------------------------------- 10. Notas visuales
NOTAS = [
    ([-480, -240], 520, 300, 4, "## VisionGuard v2.2 · Hito 2\nDisparo por turno (07/15/23 h) → Config → 4 ramas en paralelo:\n1. ResNet18 (API Python ONNX)\n2. GRU (API Python Keras)\n3. NLP almacenado (Sheets)\n4. **Transformer NLP en vivo** (HF embeddings + Python)\n\nConfig contiene URLs del panel, destinatarios y umbrales."),
    ([1680, 300], 560, 260, 3, "## Control de alucinaciones\nValidacion_Seguridad_Final: parsea JSON, verifica 11 campos, fuerza reglas de seguridad, contrasta **cada cifra** del LLM con los datos y, si el JSON es inválido, usa un **análisis determinista de respaldo**. Nunca aprueba automáticamente."),
    ([2520, 1040], 620, 220, 6, "## Punto de control humano\nUna aprobación por pieza (Loop). APROBAR / RECHAZAR por Gmail; sin respuesta en 8 h → SIN_RESPUESTA_HUMANA_ESCALAR. La decisión, su fecha y el estado se registran en Sheets y se notifican por Gmail + Telegram."),
    ([1680, -300], 520, 180, 7, "## Legado Hito 1 (deshabilitado)\n`Message a model` → `Code in JavaScript` → nodos v1.4. Se conservan como respaldo; ya no reciben datos."),
]
for pos, wd, ht, color, texto in NOTAS:
    w["nodes"].append({"parameters": {"content": texto, "height": ht, "width": wd, "color": color},
                       "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": pos,
                       "id": uid(), "name": f"Nota {len(w['nodes'])}"})

w["name"] = "VisionGuard v2.2 - Hito 2 FINAL"
w["active"] = False
w["pinData"] = {}
for k in ("id", "versionId"):
    w.pop(k, None)

# --------------------------------------------------------- 11. Salidas
importar = AQUI / "VisionGuard_v2.2_Hito2_IMPORTAR.json"
importar.write_text(json.dumps(w, indent=2, ensure_ascii=False), encoding="utf-8")

pub = copy.deepcopy(w)
pub.pop("meta", None)
for n in pub["nodes"]:
    n.pop("credentials", None)
texto = json.dumps(pub, indent=2, ensure_ascii=False)
texto = texto.replace(EMAIL, "responsable.calidad@ejemplo.com").replace(CHAT, "TU_TELEGRAM_CHAT_ID")
texto = texto.replace(SHEET_ID, "TU_SPREADSHEET_ID")
texto = re.sub(r"1xb2QV1l0-[A-Za-z0-9_-]+", "TU_FOLDER_ID_PROCESADAS", texto)
(AQUI / "VisionGuard_v2.2_Hito2_PUBLICO.json").write_text(texto, encoding="utf-8")

# ------------------------------------------------- Error handler (separado)
eh = {"name": "VisionGuard v2.2 - Error Handler", "nodes": [], "connections": {}, "active": False,
      "settings": {"executionOrder": "v1"}, "pinData": {}}
eh["nodes"] = [
    {"parameters": {}, "type": "n8n-nodes-base.errorTrigger", "typeVersion": 1, "position": [0, 0],
     "id": uid(), "name": "Error Trigger"},
    {"parameters": {"sendTo": "responsable.calidad@ejemplo.com",
                    "subject": "={{ '🚨 VisionGuard | Falla del flujo en ' + ($json.execution.lastNodeExecuted || 'nodo desconocido') }}",
                    "message": "={{ `<h2>VisionGuard | Error de ejecución</h2><p><b>Workflow:</b> ${$json.workflow.name}</p>"
                               "<p><b>Nodo:</b> ${$json.execution.lastNodeExecuted}</p><p><b>Mensaje:</b> ${String($json.execution.error?.message ?? '').slice(0, 500)}</p>"
                               "<p><b>Ejecución:</b> <a href=\"${$json.execution.url}\">${$json.execution.id}</a></p>"
                               "<p>No se generaron aprobaciones automáticas. Revise el flujo y vuelva a ejecutar.</p>` }}",
                    "options": {"appendAttribution": False}},
     "type": "n8n-nodes-base.gmail", "typeVersion": 2.2, "position": [240, -80], "id": uid(),
     "name": "Gmail_Error", "retryOnFail": True},
    {"parameters": {"chatId": "TU_TELEGRAM_CHAT_ID",
                    "text": "={{ '🚨 VisionGuard: falla en ' + $json.execution.lastNodeExecuted + '\\n' + String($json.execution.error?.message ?? '').slice(0, 300) }}",
                    "additionalFields": {"appendAttribution": False}},
     "type": "n8n-nodes-base.telegram", "typeVersion": 1.2, "position": [240, 80], "id": uid(),
     "name": "Telegram_Error", "retryOnFail": True},
]
eh["connections"] = {"Error Trigger": {"main": [[{"node": "Gmail_Error", "type": "main", "index": 0},
                                                 {"node": "Telegram_Error", "type": "main", "index": 0}]]}}
(AQUI / "VisionGuard_v2.2_Error_Handler_PUBLICO.json").write_text(json.dumps(eh, indent=2, ensure_ascii=False), encoding="utf-8")
print("OK", len(w["nodes"]), "nodos")
