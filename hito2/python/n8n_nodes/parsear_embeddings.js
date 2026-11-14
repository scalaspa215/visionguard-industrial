/*
 VISIONGUARD v2.2 - PARSEAR EMBEDDINGS  (nodo Code JS)
 Une la respuesta de Hugging Face (texto JSON) con los reportes y valida:
   - que sea una lista con un vector por reporte,
   - que todos los vectores tengan la misma dimension y sean numericos.
 Si algo falla, NO detiene el flujo: deja embeddings = null y el motivo,
 para que el nodo Python use solo las reglas y lo informe.
*/
const d = $input.first().json;
let embeddings = null;
let motivo = '';

try {
  if (d.error) throw new Error('HTTP: ' + String(d.error.message ?? d.error).slice(0, 160));
  if (d.respuesta_hf == null) throw new Error('Sin respuesta de Hugging Face');
  const v = typeof d.respuesta_hf === 'string' ? JSON.parse(d.respuesta_hf) : d.respuesta_hf;
  if (!Array.isArray(v) || v.length !== (d.reportes || []).length) {
    throw new Error(`Se esperaban ${(d.reportes || []).length} vectores y llegaron ${Array.isArray(v) ? v.length : 0}`);
  }
  const dim = v[0]?.length;
  if (!dim || !v.every(x => Array.isArray(x) && x.length === dim && x.every(Number.isFinite))) {
    throw new Error('Vectores con dimension o valores invalidos');
  }
  embeddings = v;
} catch (e) {
  motivo = e.message;
}

return [{
  json: {
    reportes: d.reportes || [],
    descartados: d.descartados || [],
    embeddings,
    dimension: embeddings ? embeddings[0].length : 0,
    motivo_sin_transformer: motivo
  }
}];
