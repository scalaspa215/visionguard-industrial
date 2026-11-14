/*
 VISIONGUARD v2.2 - PREPARAR TEXTOS NLP  (nodo Code JS)
 Entrada : filas de la pestana Reportes_NC (id_reporte, fecha, texto_reporte, rol, causa_real).
 Salida  : 1 item con la lista limpia de reportes y el cuerpo para Hugging Face.
 Validaciones: descarta filas sin id o sin texto, duplicados de id, recorta textos
 largos (600 car.) y normaliza el rol. No se envia ningun dato personal.
*/
const ROLES = ['referencia', 'prueba', 'operacion'];
const vistos = new Set();
const descartados = [];

const reportes = [];
for (const item of $input.all()) {
  const r = item.json || {};
  const id = String(r.id_reporte ?? '').trim();
  const texto = String(r.texto_reporte ?? '').replace(/\s+/g, ' ').trim();
  if (!id || !texto) { if (id || texto) descartados.push(id || '(sin id)'); continue; }
  if (vistos.has(id)) { descartados.push(id + ' (duplicado)'); continue; }
  vistos.add(id);
  let rol = String(r.rol ?? 'operacion').trim().toLowerCase();
  if (!ROLES.includes(rol)) rol = 'operacion';
  reportes.push({
    id_reporte: id,
    fecha: String(r.fecha ?? ''),
    rol,
    causa_real: rol === 'operacion' ? '' : String(r.causa_real ?? '').trim(),
    texto: texto.slice(0, 600)
  });
}

return [{
  json: {
    reportes,
    total: reportes.length,
    descartados,
    // wait_for_model evita el error 503 cuando el modelo esta "frio"
    cuerpo_hf: { inputs: reportes.map(r => r.texto), options: { wait_for_model: true } }
  }
}];
