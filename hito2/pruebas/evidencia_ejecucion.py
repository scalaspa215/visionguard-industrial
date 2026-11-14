"""
Convierte el JSON de una ejecucion n8n (descargado con la API/MCP) en una
evidencia Markdown: nodos ejecutados, estado, items y campos clave.
Anonimiza correos, chat IDs e IDs de hojas antes de escribir.
Uso: python evidencia_ejecucion.py ejecucion.json salida.md "Titulo de la prueba"
"""
import json
import re
import sys

CLAVES = ["clasificacion", "confianza", "archivo", "fuente_analisis", "prioridad", "transformer_ejecutado",
          "motivo_sin_transformer", "metodo_usado_operacion", "causa_principal_operacion", "estado",
          "decision_humana", "validacion_humana_realizada", "clave_unica", "tiene_alertas", "alertas",
          "tipo", "mejor_metodo_en_prueba_f1"]


def anonimizar(t):
    t = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", "<correo>", t)
    t = re.sub(r"\b\d{9,10}\b", "<chat_id>", t)
    return re.sub(r"spreadsheets/d/[A-Za-z0-9_-]{20,}", "spreadsheets/d/<id_hoja>", t)


def main(entrada, salida, titulo):
    d = json.load(open(entrada, encoding="utf-8"))
    ex = d["execution"]
    rd = d["data"]["resultData"]
    pin = set((rd.get("pinData") or {}).keys())
    lin = [f"# {titulo}", "",
           f"- Ejecución n8n: **{ex['id']}** · modo `{ex['mode']}` · estado **{ex['status']}**",
           f"- Inicio: {ex['startedAt']} · fin: {ex['stoppedAt']}",
           f"- Nodos con datos simulados (pin data, sin efectos externos): {len(pin)}",
           ""]
    if rd.get("error"):
        lin += [f"**Error global:** `{str(rd['error'].get('message'))[:300]}` en `{rd.get('lastNodeExecuted')}`", ""]
    lin += ["| Orden | Nodo | Estado | Items | Simulado | Campos clave |", "|---|---|---|---|---|---|"]
    filas = []
    for nodo, runs in rd["runData"].items():
        for r in runs:
            main = (r.get("data") or {}).get("main") or [[]]
            items = [it for s in main for it in (s or [])]
            campos = {}
            if items:
                j = items[0].get("json", {})
                for k in CLAVES:
                    if k in j:
                        v = j[k]
                        campos[k] = v if not isinstance(v, (dict, list)) else json.dumps(v, ensure_ascii=False)[:120]
                cs = j.get("controles_seguridad")
                if cs:
                    campos["correcciones"] = cs.get("correcciones_aplicadas")
                    campos["cifras_no_respaldadas"] = cs.get("cifras_no_respaldadas")
                mp = j.get("metricas_prueba")
                if mp:
                    campos["metricas_prueba"] = json.dumps(mp)
            estado = r.get("executionStatus", "")
            if r.get("error"):
                estado += " · " + str(r["error"].get("message"))[:120]
            filas.append((r.get("startTime", 0), nodo, estado, len(items), "sí" if nodo in pin else "no",
                          json.dumps(campos, ensure_ascii=False, default=str)[:400].replace("|", "/")))
    for i, f in enumerate(sorted(filas), 1):
        lin.append(f"| {i} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {f[5]} |")
    open(salida, "w", encoding="utf-8").write(anonimizar("\n".join(lin)) + "\n")
    print("OK", salida, len(filas), "nodos")


if __name__ == "__main__":
    main(*sys.argv[1:4])
