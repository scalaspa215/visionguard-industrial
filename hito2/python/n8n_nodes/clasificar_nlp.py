# VISIONGUARD v2.2 - CLASIFICACION NLP DE REPORTES DE NO CONFORMIDAD (nodo Code Python)
#
# Transformer: embeddings de paraphrase-multilingual-MiniLM-L12-v2 (calculados
# en Hugging Face). Clasificador por CENTROIDE: promedio normalizado de los
# reportes 'referencia' de cada causa; cada reporte va a la causa con mayor
# similitud coseno.
# Alternativa simple: reglas fijas de palabras clave (identicas a
# python/nlp/nlp_comun.py).
# Metricas: accuracy y F1 macro de AMBOS metodos sobre los reportes 'prueba'
# (no usados para construir los centroides).
#
# Sin imports: el runner Python nativo de n8n restringe la biblioteca estandar.

CLASES = ["materia_prima", "ajuste_proceso", "herramienta_molde",
          "operacion_manual", "medicion_inspeccion"]
REGLAS = {
    "materia_prima": ["porosidad", "poro", "inclusion", "aleacion", "colada", "lote de material", "impureza"],
    "ajuste_proceso": ["temperatura", "presion", "parametro", "tiempo de ciclo", "velocidad", "enfriamiento"],
    "herramienta_molde": ["molde", "matriz", "desgaste", "desgastad", "herramienta", "cavidad"],
    "operacion_manual": ["operador", "golpe", "manipulacion", "caida", "procedimiento", "turno"],
    "medicion_inspeccion": ["calibr", "medicion", "instrumento", "pie de metro", "micrometro", "galga"],
}
SIN = "sin_clasificar"
TILDES = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunaeiouun")


def leer_entrada():
    """Compatible con el runner nativo (_items) y con el antiguo Pyodide (_input)."""
    try:
        datos = _items  # noqa: F821  (variable inyectada por n8n)
    except NameError:
        datos = _input.all()  # noqa: F821
    item = datos[0]
    j = item["json"] if isinstance(item, dict) else item.json
    return j.to_py() if hasattr(j, "to_py") else j


def por_reglas(texto):
    t = str(texto).lower().translate(TILDES)
    puntos = {c: sum(1 for k in REGLAS[c] if k in t) for c in CLASES}
    mejor = max(CLASES, key=lambda c: puntos[c])
    return mejor if puntos[mejor] > 0 else SIN


def unitario(v):
    n = sum(x * x for x in v) ** 0.5
    return [x / n for x in v] if n > 0 else v


def metricas(reales, pred):
    n = len(reales)
    if n == 0:
        return {"n": 0, "accuracy": None, "f1_macro": None}
    acc = sum(1 for r, p in zip(reales, pred) if r == p) / n
    f1s = []
    for c in CLASES:
        tp = sum(1 for r, p in zip(reales, pred) if r == c and p == c)
        fp = sum(1 for r, p in zip(reales, pred) if r != c and p == c)
        fn = sum(1 for r, p in zip(reales, pred) if r == c and p != c)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    return {"n": n, "accuracy": round(acc, 4), "f1_macro": round(sum(f1s) / len(f1s), 4)}


d = leer_entrada()
reportes = d.get("reportes") or []
emb = d.get("embeddings")
usar_tf = bool(emb) and len(emb) == len(reportes)
motivo = d.get("motivo_sin_transformer") or ("" if usar_tf else "Sin embeddings")

# 1. Reglas para todos los reportes
for r in reportes:
    r["causa_reglas"] = por_reglas(r.get("texto", ""))

# 2. Transformer: centroides con los reportes de referencia
if usar_tf:
    vect = [unitario(v) for v in emb]
    centroides = {}
    for c in CLASES:
        grupo = [vect[i] for i, r in enumerate(reportes) if r["rol"] == "referencia" and r["causa_real"] == c]
        if grupo:
            centroides[c] = unitario([sum(col) / len(grupo) for col in zip(*grupo)])
    if len(centroides) < 2:
        usar_tf, motivo = False, "Menos de 2 causas con reportes de referencia"
    else:
        for i, r in enumerate(reportes):
            sims = {c: sum(a * b for a, b in zip(vect[i], cv)) for c, cv in centroides.items()}
            mejor = max(sims, key=sims.get)
            r["causa_transformer"] = mejor
            r["similitud"] = round(sims[mejor], 4)

# 3. Metricas en el conjunto de prueba (mismos datos para ambos metodos)
prueba = [r for r in reportes if r["rol"] == "prueba" and r["causa_real"] in CLASES]
reales = [r["causa_real"] for r in prueba]
m_reglas = metricas(reales, [r["causa_reglas"] for r in prueba])
m_tf = metricas(reales, [r.get("causa_transformer", SIN) for r in prueba]) if usar_tf else None
if m_tf and m_tf["accuracy"] is not None and m_reglas["accuracy"] is not None:
    ganador = ("Transformer" if m_tf["f1_macro"] > m_reglas["f1_macro"]
               else "Reglas" if m_tf["f1_macro"] < m_reglas["f1_macro"] else "Empate")
else:
    ganador = "No evaluable"

# 4. Reportes de operacion (los "nuevos" del turno)
oper = [r for r in reportes if r["rol"] == "operacion"]
# Navaja de Occam: para los reportes nuevos se usa el metodo con MEJOR F1 en
# prueba en esta misma corrida (en la evaluacion offline ganaron las reglas).
clave = "causa_transformer" if usar_tf and ganador == "Transformer" else "causa_reglas"
dist = {}
for r in oper:
    dist[r[clave]] = dist.get(r[clave], 0) + 1
principal = max(dist, key=dist.get) if dist else "sin_datos"
concord = (round(100 * sum(1 for r in oper if r.get("causa_transformer") == r["causa_reglas"]) / len(oper), 1)
           if usar_tf and oper else None)
casos = sorted(oper, key=lambda r: r.get("fecha", ""), reverse=True)[:8]

return [{"json": {
    "tipo": "NLP_TRANSFORMER",
    "modulo": "Transformer_NLP_Clasificacion",
    "transformer_ejecutado": usar_tf,
    "modelo": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" if usar_tf else "reglas_palabras_clave",
    "metodo": "centroide_coseno_sobre_embeddings" if usar_tf else "reglas_palabras_clave",
    "motivo_sin_transformer": "" if usar_tf else motivo,
    "n_referencia": sum(1 for r in reportes if r["rol"] == "referencia"),
    "n_prueba": len(prueba),
    "n_operacion": len(oper),
    "metricas_prueba": {"transformer": m_tf, "reglas": m_reglas},
    "mejor_metodo_en_prueba_f1": ganador,
    "metodo_usado_operacion": "Transformer" if clave == "causa_transformer" else "Reglas",
    "distribucion_causas_operacion": dist,
    "causa_principal_operacion": principal,
    "concordancia_transformer_reglas_pct": concord,
    "casos_operacion": [{"id_reporte": r["id_reporte"], "fecha": r.get("fecha", ""),
                         "causa_transformer": r.get("causa_transformer"), "similitud": r.get("similitud"),
                         "causa_reglas": r["causa_reglas"]} for r in casos],
    "descartados_validacion": d.get("descartados") or [],
    "origen": "SIMULADO_ACADEMICO_NO_REAL",
}}]
