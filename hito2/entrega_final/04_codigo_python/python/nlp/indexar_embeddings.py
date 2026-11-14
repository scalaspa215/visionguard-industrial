"""
VisionGuard Industrial - Hito 2
Indexacion de los reportes NC con el Transformer MiniLM (paso batch de un RAG).

Calcula UNA VEZ los embeddings de paraphrase-multilingual-MiniLM-L12-v2 para
todos los reportes de reportes_nc_simulados.csv y los guarda en
embeddings_nc_minilm.json. El workflow n8n lo descarga desde GitHub y lo usa
cuando la llamada en vivo a Hugging Face no esta disponible.

Integridad: cada vector va con un hash djb2 del texto normalizado (espacios
colapsados, recortado a 600 caracteres, igual que Preparar_Textos_NLP). Si el
texto de la hoja cambia, el hash no coincide y ese reporte no usa el indice.

Uso: pip install sentence-transformers ; python indexar_embeddings.py
"""
import csv
import json
import re
from datetime import date
from pathlib import Path

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
AQUI = Path(__file__).parent


def normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", str(t or "")).strip()[:600]


def djb2(t: str) -> int:
    """Mismo algoritmo que parsear_embeddings.js (entero de 32 bits sin signo)."""
    h = 5381
    for ch in t:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return h


def main():
    from sentence_transformers import SentenceTransformer
    filas = list(csv.DictReader((AQUI / "reportes_nc_simulados.csv").open(encoding="utf-8")))
    textos = [normalizar(f["texto_reporte"]) for f in filas]
    modelo = SentenceTransformer(MODELO)
    vect = modelo.encode(textos, normalize_embeddings=True)
    indice = {
        "modelo": MODELO,
        "dimension": int(vect.shape[1]),
        "normalizado": True,
        "generado": str(date.today()),
        "origen_textos": "reportes_nc_simulados.csv (SIMULADO_ACADEMICO_NO_REAL)",
        "vectores": {f["id_reporte"]: {"hash": djb2(t), "v": [round(float(x), 5) for x in v]}
                     for f, t, v in zip(filas, textos, vect)},
    }
    out = AQUI / "embeddings_nc_minilm.json"
    out.write_text(json.dumps(indice, separators=(",", ":")), encoding="utf-8")
    print("OK", len(filas), "vectores de", indice["dimension"], "dims ->", out.name, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
