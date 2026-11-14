"""
VisionGuard Industrial - Hito 2
Evaluacion NLP: Transformer (embeddings multilingues) vs reglas fijas.

Mismos datos de prueba (rol == 'prueba') y misma metrica para ambos.
  * Reglas: nlp_comun.clasificar_por_reglas (no requiere instalar nada).
  * Transformer: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    (encoder tipo BERT con auto-atencion, 12 capas). Clasificador por
    centroide: se promedian los embeddings de los reportes 'referencia' de
    cada causa y cada reporte de prueba se asigna al centroide mas parecido
    (similitud coseno). Es el MISMO metodo que ejecuta el nodo Python de n8n.

Uso:
  python evaluar_nlp.py                 # reglas + Transformer si esta instalado
  pip install sentence-transformers     # (Colab ya lo trae) para el Transformer
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nlp_comun import CLASES, clasificar_por_reglas, metricas  # noqa: E402

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
AQUI = Path(__file__).parent


def cargar():
    with (AQUI / "reportes_nc_simulados.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def evaluar_transformer(ref, prueba):
    from sentence_transformers import SentenceTransformer
    import numpy as np
    modelo = SentenceTransformer(MODELO)
    emb_ref = modelo.encode([r["texto_reporte"] for r in ref], normalize_embeddings=True)
    emb_pru = modelo.encode([r["texto_reporte"] for r in prueba], normalize_embeddings=True)
    centroides = []
    for c in CLASES:
        v = emb_ref[[i for i, r in enumerate(ref) if r["causa_real"] == c]].mean(axis=0)
        centroides.append(v / np.linalg.norm(v))
    sims = emb_pru @ np.stack(centroides).T
    return [CLASES[int(i)] for i in sims.argmax(axis=1)], sims.max(axis=1).tolist()


def main():
    filas = cargar()
    ref = [r for r in filas if r["rol"] == "referencia"]
    prueba = [r for r in filas if r["rol"] == "prueba"]
    reales = [r["causa_real"] for r in prueba]

    pred_reglas = [clasificar_por_reglas(r["texto_reporte"]) for r in prueba]
    resultado = {"datos": "SIMULADOS_ACADEMICOS", "n_referencia": len(ref), "n_prueba": len(prueba),
                 "reglas": metricas(reales, pred_reglas)}
    try:
        pred_tf, sims = evaluar_transformer(ref, prueba)
        resultado["transformer"] = metricas(reales, pred_tf)
        resultado["transformer"]["modelo"] = MODELO
        errores = [(r["id_reporte"], r["causa_real"], p) for r, p in zip(prueba, pred_tf) if p != r["causa_real"]]
        resultado["transformer"]["errores"] = errores
    except ImportError:
        resultado["transformer"] = "NO_EJECUTADO: falta sentence-transformers (ejecutar en Colab)"

    resultado["reglas"]["errores"] = [(r["id_reporte"], r["causa_real"], p)
                                      for r, p in zip(prueba, pred_reglas) if p != r["causa_real"]]
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    (AQUI / "resultados_nlp.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
