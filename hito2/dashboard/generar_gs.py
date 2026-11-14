"""Inserta en el Apps Script la evidencia calculada (resultados_*.json) y los reportes NC.
Uso: python generar_gs.py  -> VisionGuard_Dashboard_Sheets.gs (listo para pegar)."""
import csv
import json
from pathlib import Path

AQUI = Path(__file__).parent
PY = AQUI.parent / "python"
series = json.loads((PY / "series" / "resultados_series.json").read_text(encoding="utf-8"))
nlp = json.loads((PY / "nlp" / "resultados_nlp.json").read_text(encoding="utf-8"))
roi = json.loads((PY / "negocio" / "roi_resultados.json").read_text(encoding="utf-8"))

mae = {}
for m in series["metricas"]:
    mae.setdefault(m["modelo"], {})[m["conjunto"]] = m
orden = sorted(mae, key=lambda k: mae[k]["test"]["MAE_pp"])
ev = {
    "series": [["Modelo", "MAE validación", "MAE prueba"]] +
              [[k, mae[k]["val"]["MAE_pp"], mae[k]["test"]["MAE_pp"]] for k in orden],
    "series_tabla": [["Serie (1 día, pp)", "MAE val", "MAE prueba", "RMSE prueba"]] +
                    [[k, mae[k]["val"]["MAE_pp"], mae[k]["test"]["MAE_pp"], mae[k]["test"]["RMSE_pp"]] for k in orden],
    "nlp": [["Método", "Accuracy", "F1 macro"], ["Reglas fijas", nlp["reglas"]["accuracy"], nlp["reglas"]["f1_macro"]]],
    "roi": [["Escenario", "ROI año 1 (%)"]] + [[k, v["roi_anio1_pct"]] for k, v in roi["escenarios"].items()],
    "resnet": [["ResNet18 · test 715 img.", "Umbral simple", "ResNet18", "Fuente"],
               ["Accuracy", 0.6951, 0.9776, "Colab Hito 1"],
               ["Precisión defectuosa", 0.7818, 0.9932, "Colab Hito 1"],
               ["Recall defectuosa", 0.7196, 0.9713, "Colab Hito 1"],
               ["F1 defectuosa", 0.7494, 0.9821, "Colab Hito 1"],
               ["Falsos negativos", "—", "13 de 453", "Colab Hito 1"]],
    "recuperacion_base": roi["escenarios"]["Base"]["recuperacion_meses"],
    "nota": "Series: datos simulados, 81 puntos de prueba; GRU consultado en su API real. "
            "NLP: 40 reportes NC simulados de prueba. ROI: estimación académica con supuestos explícitos.",
}
if isinstance(nlp.get("transformer"), dict):
    ev["nlp"].append(["Transformer (MiniLM)", nlp["transformer"]["accuracy"], nlp["transformer"]["f1_macro"]])

with (PY / "nlp" / "reportes_nc_simulados.csv").open(encoding="utf-8") as f:
    filas = list(csv.reader(f))

plantilla = (AQUI / "VisionGuard_Dashboard_Sheets.template.gs").read_text(encoding="utf-8")
salida = (plantilla.replace("__EVIDENCIA__", json.dumps(ev, ensure_ascii=False))
          .replace("__REPORTES_NC__", json.dumps(filas, ensure_ascii=False)))
(AQUI / "VisionGuard_Dashboard_Sheets.gs").write_text(salida, encoding="utf-8")
print("OK", len(filas) - 1, "reportes NC;", len(ev["series"]) - 1, "modelos de serie")
