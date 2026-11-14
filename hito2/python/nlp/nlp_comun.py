"""
VisionGuard Industrial - Hito 2
Modulo NLP comun: clases de causa, reglas fijas (alternativa simple) y metricas.

La MISMA logica de reglas se usa en:
  - este script (evaluacion offline), y
  - el nodo Python `Clasificar_NLP_Python` del workflow n8n.
Si se modifica aqui, debe modificarse alla (y viceversa).
"""
import unicodedata

# Cinco causas de no conformidad (NC) en fundicion de piezas metalicas.
CLASES = [
    "materia_prima",       # porosidad, inclusiones, aleacion fuera de especificacion
    "ajuste_proceso",      # temperatura, presion, tiempos, parametros de maquina
    "herramienta_molde",   # molde/matriz/herramienta desgastada o danada
    "operacion_manual",    # manipulacion, golpes, procedimiento no seguido
    "medicion_inspeccion", # instrumento descalibrado, error de medicion
]

# Alternativa simple (Navaja de Occam): palabras clave fijadas A PRIORI,
# antes de generar los textos de prueba. No se ajustaron mirando el resultado.
REGLAS = {
    "materia_prima": ["porosidad", "poro", "inclusion", "aleacion", "colada", "lote de material", "impureza"],
    "ajuste_proceso": ["temperatura", "presion", "parametro", "tiempo de ciclo", "velocidad", "enfriamiento"],
    "herramienta_molde": ["molde", "matriz", "desgaste", "desgastad", "herramienta", "cavidad"],
    "operacion_manual": ["operador", "golpe", "manipulacion", "caida", "procedimiento", "turno"],
    "medicion_inspeccion": ["calibr", "medicion", "instrumento", "pie de metro", "micrometro", "galga"],
}

SIN_CLASE = "sin_clasificar"


def normalizar(texto: str) -> str:
    """Minusculas y sin tildes, para que 'Inclusión' == 'inclusion'."""
    t = unicodedata.normalize("NFKD", str(texto or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def clasificar_por_reglas(texto: str) -> str:
    """Cuenta coincidencias de palabras clave; gana la clase con mas aciertos.
    Empate -> primera clase en el orden de CLASES. Sin aciertos -> sin_clasificar."""
    t = normalizar(texto)
    puntajes = {c: sum(1 for k in REGLAS[c] if k in t) for c in CLASES}
    mejor = max(CLASES, key=lambda c: puntajes[c])
    return mejor if puntajes[mejor] > 0 else SIN_CLASE


def metricas(reales, predichas, clases=CLASES):
    """Accuracy y F1 macro implementados a mano (sin dependencias)."""
    n = len(reales)
    acc = sum(r == p for r, p in zip(reales, predichas)) / n if n else 0.0
    f1s = []
    for c in clases:
        tp = sum(r == c and p == c for r, p in zip(reales, predichas))
        fp = sum(r != c and p == c for r, p in zip(reales, predichas))
        fn = sum(r == c and p != c for r, p in zip(reales, predichas))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return {"n": n, "accuracy": round(acc, 4), "f1_macro": round(sum(f1s) / len(f1s), 4),
            "sin_clasificar": sum(p == SIN_CLASE for p in predichas)}
