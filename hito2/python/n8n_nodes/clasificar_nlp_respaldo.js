/*
 VISIONGUARD v2.2 - CLASIFICACION NLP (RESPALDO EN JAVASCRIPT)
 Traduccion 1:1 de clasificar_nlp.py. Usar SOLO si la instancia n8n no
 permite Python: habilitar este nodo, deshabilitar Clasificar_NLP_Python y
 conectar este nodo a la entrada 4 del Merge.
*/
const CLASES = ['materia_prima', 'ajuste_proceso', 'herramienta_molde', 'operacion_manual', 'medicion_inspeccion'];
const REGLAS = {
  materia_prima: ['porosidad', 'poro', 'inclusion', 'aleacion', 'colada', 'lote de material', 'impureza'],
  ajuste_proceso: ['temperatura', 'presion', 'parametro', 'tiempo de ciclo', 'velocidad', 'enfriamiento'],
  herramienta_molde: ['molde', 'matriz', 'desgaste', 'desgastad', 'herramienta', 'cavidad'],
  operacion_manual: ['operador', 'golpe', 'manipulacion', 'caida', 'procedimiento', 'turno'],
  medicion_inspeccion: ['calibr', 'medicion', 'instrumento', 'pie de metro', 'micrometro', 'galga']
};
const SIN = 'sin_clasificar';
const norm = t => String(t ?? '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
const porReglas = t => {
  const s = norm(t);
  const p = Object.fromEntries(CLASES.map(c => [c, REGLAS[c].filter(k => s.includes(k)).length]));
  const mejor = CLASES.reduce((a, b) => (p[b] > p[a] ? b : a));
  return p[mejor] > 0 ? mejor : SIN;
};
const unit = v => { const n = Math.sqrt(v.reduce((s, x) => s + x * x, 0)); return n > 0 ? v.map(x => x / n) : v; };
const metricas = (reales, pred) => {
  const n = reales.length;
  if (!n) return { n: 0, accuracy: null, f1_macro: null };
  const acc = reales.filter((r, i) => r === pred[i]).length / n;
  const f1 = CLASES.map(c => {
    const tp = reales.filter((r, i) => r === c && pred[i] === c).length;
    const fp = reales.filter((r, i) => r !== c && pred[i] === c).length;
    const fn = reales.filter((r, i) => r === c && pred[i] !== c).length;
    const pr = tp + fp ? tp / (tp + fp) : 0, rc = tp + fn ? tp / (tp + fn) : 0;
    return pr + rc ? 2 * pr * rc / (pr + rc) : 0;
  });
  return { n, accuracy: +acc.toFixed(4), f1_macro: +(f1.reduce((a, b) => a + b, 0) / f1.length).toFixed(4) };
};

const d = $input.first().json;
const reportes = (d.reportes || []).map(r => ({ ...r, causa_reglas: porReglas(r.texto) }));
let usarTf = Array.isArray(d.embeddings) && d.embeddings.length === reportes.length && reportes.length > 0;
let motivo = d.motivo_sin_transformer || (usarTf ? '' : 'Sin embeddings');

if (usarTf) {
  const vect = d.embeddings.map(unit);
  const cent = {};
  for (const c of CLASES) {
    const g = vect.filter((v, i) => reportes[i].rol === 'referencia' && reportes[i].causa_real === c);
    if (g.length) cent[c] = unit(g[0].map((_, j) => g.reduce((s, v) => s + v[j], 0) / g.length));
  }
  if (Object.keys(cent).length < 2) { usarTf = false; motivo = 'Menos de 2 causas con reportes de referencia'; }
  else reportes.forEach((r, i) => {
    let mejor = null, sim = -2;
    for (const [c, cv] of Object.entries(cent)) {
      const s = vect[i].reduce((a, x, j) => a + x * cv[j], 0);
      if (s > sim) { sim = s; mejor = c; }
    }
    r.causa_transformer = mejor; r.similitud = +sim.toFixed(4);
  });
}

const prueba = reportes.filter(r => r.rol === 'prueba' && CLASES.includes(r.causa_real));
const reales = prueba.map(r => r.causa_real);
const mReglas = metricas(reales, prueba.map(r => r.causa_reglas));
const mTf = usarTf ? metricas(reales, prueba.map(r => r.causa_transformer ?? SIN)) : null;
const ganador = mTf && mTf.accuracy !== null && mReglas.accuracy !== null
  ? (mTf.f1_macro > mReglas.f1_macro ? 'Transformer' : mTf.f1_macro < mReglas.f1_macro ? 'Reglas' : 'Empate')
  : 'No evaluable';
const oper = reportes.filter(r => r.rol === 'operacion');
// Navaja de Occam: se usa el metodo con mejor F1 en prueba en esta corrida.
const clave = usarTf && ganador === 'Transformer' ? 'causa_transformer' : 'causa_reglas';
const dist = {};
oper.forEach(r => { dist[r[clave]] = (dist[r[clave]] || 0) + 1; });
const principal = Object.keys(dist).length ? Object.keys(dist).reduce((a, b) => (dist[b] > dist[a] ? b : a)) : 'sin_datos';
const concord = usarTf && oper.length
  ? +(100 * oper.filter(r => r.causa_transformer === r.causa_reglas).length / oper.length).toFixed(1) : null;

return [{ json: {
  tipo: 'NLP_TRANSFORMER', modulo: 'Transformer_NLP_Clasificacion', transformer_ejecutado: usarTf,
  modelo: usarTf ? 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2' : 'reglas_palabras_clave',
  metodo: usarTf ? 'centroide_coseno_sobre_embeddings' : 'reglas_palabras_clave',
  motivo_sin_transformer: usarTf ? '' : motivo,
  n_referencia: reportes.filter(r => r.rol === 'referencia').length, n_prueba: prueba.length, n_operacion: oper.length,
  metricas_prueba: { transformer: mTf, reglas: mReglas }, mejor_metodo_en_prueba_f1: ganador,
  metodo_usado_operacion: clave === 'causa_transformer' ? 'Transformer' : 'Reglas',
  distribucion_causas_operacion: dist, causa_principal_operacion: principal,
  concordancia_transformer_reglas_pct: concord,
  casos_operacion: [...oper].sort((a, b) => String(b.fecha).localeCompare(String(a.fecha))).slice(0, 8)
    .map(r => ({ id_reporte: r.id_reporte, fecha: r.fecha, causa_transformer: r.causa_transformer ?? null,
                 similitud: r.similitud ?? null, causa_reglas: r.causa_reglas })),
  descartados_validacion: d.descartados || [], origen: 'SIMULADO_ACADEMICO_NO_REAL'
} }];
