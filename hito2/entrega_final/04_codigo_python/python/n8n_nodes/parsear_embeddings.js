/*
 VISIONGUARD v2.2 - PARSEAR EMBEDDINGS  (nodo Code JS)
 Fuentes de embeddings del Transformer MiniLM, en orden de preferencia:
   1. HF_EN_VIVO: respuesta de Hugging Face (Embeddings_Transformer_HF).
   2. INDICE_PRECALCULADO: indice batch generado con el MISMO modelo
      (python/nlp/indexar_embeddings.py) y descargado desde GitHub por
      Indice_Embeddings_GitHub. Cada vector se usa solo si el hash del texto
      coincide (integridad: el reporte no cambio desde la indexacion).
 Validaciones: un vector por reporte, misma dimension y valores numericos.
 Si nada sirve: embeddings = null y motivo, y el nodo Python usa solo reglas.
*/
const d = $('Unir_Textos_Embeddings').first().json;
// raw.githubusercontent.com responde text/plain: n8n deja el cuerpo como texto en `data`
// (verificado en la ejecucion 110). Se parsea aqui.
let idx = $input.first().json;
if (!idx.vectores && typeof idx.data === 'string') {
  try { idx = JSON.parse(idx.data); } catch (e) { idx = { error: { message: 'indice no es JSON valido' } }; }
}
const reportes = d.reportes || [];

// djb2 de 32 bits sin signo (identico a indexar_embeddings.py)
function djb2(t) {
  let h = 5381;
  for (const ch of t) h = (Math.imul(h, 33) ^ ch.charCodeAt(0)) >>> 0;
  return h;
}
function validos(v, n) {
  if (!Array.isArray(v) || v.length !== n || n === 0) return false;
  const dim = v[0]?.length;
  return !!dim && v.every(x => Array.isArray(x) && x.length === dim && x.every(Number.isFinite));
}

let embeddings = null, origen = 'NINGUNO';
const motivos = [];

// 1. Hugging Face en vivo
try {
  if (d.error) throw new Error('HF: ' + String(d.error.message ?? d.error).slice(0, 120));
  if (d.respuesta_hf == null) throw new Error('HF: sin respuesta');
  const v = typeof d.respuesta_hf === 'string' ? JSON.parse(d.respuesta_hf) : d.respuesta_hf;
  if (!validos(v, reportes.length)) throw new Error('HF: vectores invalidos o incompletos');
  embeddings = v; origen = 'HF_EN_VIVO';
} catch (e) { motivos.push(e.message); }

// 2. Indice precalculado (GitHub)
if (!embeddings) {
  try {
    if (idx.error) throw new Error('Indice: ' + String(idx.error.message ?? idx.error).slice(0, 120));
    const tabla = idx.vectores || {};
    const v = reportes.map(r => {
      const e = tabla[r.id_reporte];
      return e && e.hash === djb2(r.texto) ? e.v : null;
    });
    const faltan = v.filter(x => !x).length;
    if (faltan) throw new Error(`Indice: ${faltan} reporte(s) sin vector o con texto modificado`);
    if (!validos(v, reportes.length)) throw new Error('Indice: vectores invalidos');
    embeddings = v; origen = 'INDICE_PRECALCULADO';
  } catch (e) { motivos.push(e.message); }
}

return [{
  json: {
    reportes,
    descartados: d.descartados || [],
    embeddings,
    dimension: embeddings ? embeddings[0].length : 0,
    origen_embeddings: origen,
    modelo_indice: idx.modelo || null,
    motivo_sin_transformer: embeddings ? '' : motivos.join(' | ')
  }
}];
