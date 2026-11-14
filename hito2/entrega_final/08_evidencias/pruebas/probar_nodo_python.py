"""
Ejecuta el nodo Python de n8n (clasificar_nlp.py) fuera de n8n y compara su
salida con la del respaldo JavaScript sobre la misma entrada.
Requiere haber corrido antes: node harness_nodos.js
"""
import json
from pathlib import Path

AQUI = Path(__file__).parent
codigo = (AQUI.parent / "python" / "n8n_nodes" / "clasificar_nlp.py").read_text(encoding="utf-8")
entrada = json.loads((AQUI / "entrada_python_nlp.json").read_text(encoding="utf-8"))

# n8n envuelve el codigo en una funcion; replicamos eso para permitir el 'return'.
cuerpo = "\n".join("    " + l for l in codigo.splitlines())
ns = {}
exec("def nodo(_items):\n" + cuerpo, ns)
salida_py = ns["nodo"]([{"json": entrada}])[0]["json"]
salida_js = json.loads((AQUI / "salida_js_nlp.json").read_text(encoding="utf-8"))

claves = ["transformer_ejecutado", "metricas_prueba", "distribucion_causas_operacion",
          "causa_principal_operacion", "concordancia_transformer_reglas_pct", "mejor_metodo_en_prueba_f1"]
iguales = {k: salida_py[k] == salida_js[k] for k in claves}
print(json.dumps({"iguales": iguales, "py": {k: salida_py[k] for k in claves}}, indent=1, ensure_ascii=False))
print("PYTHON == JS:", all(iguales.values()))
