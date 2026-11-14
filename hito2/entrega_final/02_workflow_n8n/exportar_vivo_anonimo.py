"""
Exporta el workflow VIVO de n8n (respuesta de get_workflow_details / API) a un
JSON importable y ANONIMIZADO: sin credenciales, correo, chat ID, IDs de hojas
o carpetas, ni metadatos de la instancia.
Uso: python exportar_vivo_anonimo.py respuesta_mcp.json salida.json
"""
import json
import re
import sys

entrada, salida = sys.argv[1], sys.argv[2]
d = json.load(open(entrada, encoding="utf-8"))
w = d.get("workflow", d)
pub = {k: w[k] for k in ("name", "nodes", "connections", "settings") if k in w}
pub["pinData"] = {}
pub["settings"] = {k: v for k, v in (pub.get("settings") or {}).items() if k != "errorWorkflow"}
for n in pub["nodes"]:
    n.pop("credentials", None)
texto = json.dumps(pub, indent=2, ensure_ascii=False)
texto = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", "responsable.calidad@ejemplo.com", texto)
texto = re.sub(r'"(chatId|value)": "\d{8,12}"', r'"\1": "TU_TELEGRAM_CHAT_ID"', texto)
texto = re.sub(r"\b\d{9,10}\b(?=[\"'])", "TU_TELEGRAM_CHAT_ID", texto)
texto = re.sub(r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "spreadsheets/d/TU_SPREADSHEET_ID", texto)
texto = re.sub(r'"value": "1[A-Za-z0-9_-]{30,}"', '"value": "TU_ID_GOOGLE"', texto)
texto = re.sub(r"drive/folders/[A-Za-z0-9_-]{20,}", "drive/folders/TU_FOLDER_ID", texto)
open(salida, "w", encoding="utf-8").write(texto)
print("OK", salida, len(pub["nodes"]), "nodos")
