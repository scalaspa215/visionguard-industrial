"""
Arma hito2/entrega_final/ (version PUBLICA, sin datos personales) a partir de entrega/.
Uso: python armar_entrega_final.py <destino>   (p. ej. ../repo/hito2/entrega_final)
"""
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).parent
DEST = Path(sys.argv[1]).resolve()
if DEST.exists():
    shutil.rmtree(DEST)

MAPA = {
    "01_informe": ["docs/INFORME_TECNICO_HITO2.docx", "docs/INFORME_TECNICO_HITO2.pdf", "docs/INFORME_TECNICO_HITO2.md"],
    "02_workflow_n8n": ["n8n/VisionGuard_v2.2_Hito2_FINAL_vivo_PUBLICO.json", "n8n/VisionGuard_v2.2_Hito2_PUBLICO.json",
                        "n8n/build_workflow_v22.py", "n8n/exportar_vivo_anonimo.py"],
    "03_error_handler": ["n8n/VisionGuard_v2.2_Error_Handler_PUBLICO.json"],
    "04_codigo_python": ["python"],
    "05_notebooks": ["notebooks"],
    "06_comparacion_modelos": ["python/series/resultados_series.json", "python/series/predicciones_series.csv",
                               "python/nlp/resultados_nlp.json"],
    "07_negocio_roi": ["python/negocio/roi_resultados.json", "python/negocio/roi_escenarios.csv",
                       "python/negocio/roi_escenarios.png"],
    "08_evidencias": ["evidencias", "pruebas", "docs/PLAN_PRUEBAS_Y_EVIDENCIAS.md"],
    "09_matriz_cumplimiento": ["docs/MATRIZ_CUMPLIMIENTO.md"],
    "10_presentacion_defensa": ["docs/VisionGuard_Hito2_Presentacion.pptx", "docs/GUION_DEMO_15MIN.md"],
    "11_tablero": ["dashboard/VisionGuard_Dashboard_Sheets.gs", "docs/GUIA_IMPLEMENTACION_N8N.md"],
}
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", "*IMPORTAR*")
for carpeta, fuentes in MAPA.items():
    d = DEST / carpeta
    d.mkdir(parents=True, exist_ok=True)
    for f in fuentes:
        src = AQUI / f
        if src.is_dir():
            shutil.copytree(src, d / src.name, ignore=IGNORAR, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, d / src.name)
        else:
            print("FALTA", f)
shutil.copy2(AQUI / "README_ENTREGA_FINAL.md", DEST / "README.md")

# Barrido de seguridad: ningun correo, chat ID ni ID de hoja en texto
PATRONES = [r"[A-Za-z0-9._%+-]+@gmail\.com", r"BEGIN PRIV[A]TE KEY", r"hf_[A-Za-z0-9]{20,}", r"sk-[A-Za-z0-9]{20,}"]
# Valores privados (chat ID, ID de hoja) leidos del export privado, sin escribirlos aqui.
_priv = AQUI / "n8n" / "VisionGuard_v2.2_Hito2_IMPORTAR.json"
if _priv.exists():
    import json as _json
    _w = _json.loads(_priv.read_text(encoding="utf-8"))
    _cfg = next(n for n in _w["nodes"] if n["name"] == "Config")["parameters"]["assignments"]["assignments"]
    PATRONES.append(re.escape(str(next(a["value"] for a in _cfg if a["name"] == "telegram_chat_id"))))
    _sheet = re.search(r"spreadsheets/d/([A-Za-z0-9_-]{20,})", _json.dumps(_w))
    if _sheet:
        PATRONES.append(re.escape(_sheet.group(1)))
problemas = []
for p in DEST.rglob("*"):
    if p.is_file() and p.suffix.lower() in {".json", ".md", ".py", ".js", ".gs", ".ipynb", ".csv", ".txt"}:
        t = p.read_text(encoding="utf-8", errors="ignore")
        for pat in PATRONES:
            if re.search(pat, t):
                problemas.append(f"{p.relative_to(DEST)}: {pat}")
print("archivos:", sum(1 for p in DEST.rglob('*') if p.is_file()))
print("PROBLEMAS:" if problemas else "Barrido de seguridad OK", *problemas, sep="\n  ")
