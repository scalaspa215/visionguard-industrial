/*
 VisionGuard v2.2 - Pruebas unitarias de los nodos Code (fuera de n8n).
 Emula $input, $('Nodo') y $now para ejecutar el MISMO codigo que va en el workflow.
 Uso: node harness_nodos.js   (genera resultados_pruebas_nodos.json)
*/
const fs = require('fs');
const path = require('path');
const DIR = path.join(__dirname, '..', 'python', 'n8n_nodes');
const leer = f => fs.readFileSync(path.join(DIR, f), 'utf8');

const nowStub = { setZone: () => ({ toFormat: f => (f.includes('HH') ? '2026-11-14 12:00:00' : '2026-11-14') }) };

function ejecutar(archivo, entrada, nodos) {
  const $input = { all: () => entrada.map(j => ({ json: j })), first: () => ({ json: entrada[0] }) };
  const $ = nombre => {
    if (!(nombre in nodos)) throw new Error(`Referenced node is unexecuted: ${nombre}`);
    const items = nodos[nombre].map(j => ({ json: j }));
    return { all: () => items, first: () => items[0] };
  };
  const fn = new Function('$input', '$', '$now', leer(archivo));
  return fn($input, $, nowStub).map(i => i.json);
}

const config = { umbral_confianza: 0.9, umbral_pronostico_pct: 7.5, umbral_discrepancia_pp: 1.5 };
const gru = { tipo: 'RESUMEN_GRU', total_lineas: 3, linea_mayor_pronostico: 'L3', mayor_pronostico_pct: 7.89,
  pronosticos: [
    { linea: 'L1', fecha_pronostico: '2026-10-28', gru_pct: 4.09, promedio_movil_pct: 4.57 },
    { linea: 'L2', fecha_pronostico: '2026-10-28', gru_pct: 6.48, promedio_movil_pct: 8.05 },
    { linea: 'L3', fecha_pronostico: '2026-10-28', gru_pct: 7.89, promedio_movil_pct: 7.83 }] };
const nlpOk = { tipo: 'NLP_TRANSFORMER', transformer_ejecutado: true, modelo: 'MiniLM', metodo: 'centroide',
  metricas_prueba: { transformer: { n: 40, accuracy: 0.8, f1_macro: 0.79 }, reglas: { n: 40, accuracy: 0.425, f1_macro: 0.5154 } },
  mejor_metodo_en_prueba_f1: 'Transformer', n_operacion: 20, distribucion_causas_operacion: { materia_prima: 5 },
  causa_principal_operacion: 'materia_prima', concordancia_transformer_reglas_pct: 55, casos_operacion: [] };
const img = (archivo, clas, conf, rev) => ({ archivo, modelo: 'ResNet18', clasificacion: clas, confianza: conf,
  probabilidades: { correcta: clas === 'Correcta' ? conf : 1 - conf, defectuosa: clas === 'Defectuosa' ? conf : 1 - conf },
  decision_sugerida: 'X', requiere_revision_humana: rev });

const resultados = [];
function caso(nombre, f) {
  try { const r = f(); resultados.push({ caso: nombre, ok: r.ok, detalle: r.detalle }); }
  catch (e) { resultados.push({ caso: nombre, ok: false, detalle: 'EXCEPCION: ' + e.message }); }
}
const llmResp = obj => ({ output: [{ content: [{ type: 'output_text', text: typeof obj === 'string' ? obj : JSON.stringify(obj) }] }] });
const base = {
  diagnostico: 'ResNet18 clasifico VG_T1.jpeg como Defectuosa con 99.63 % de confianza. GRU simulado: L3 7.89 %.',
  recomendacion: 'Apartar la pieza e inspeccionar. No aprobar automaticamente.', prioridad: 'alta',
  justificacion: 'Clasificacion defectuosa.', resumen_imagenes: '1 imagen defectuosa.',
  resumen_series_temporales: 'L1 4.09 %, L2 6.48 %, L3 7.89 % (simulado).', resumen_nlp: 'Transformer F1 0.79 vs reglas 0.5154.',
  riesgos_limitaciones: 'Datos simulados.', requiere_revision_humana: true, aprobacion_automatica: false,
  origen: 'PROTOTIPO_ACADEMICO_CON_DATOS_SIMULADOS' };

function cadena(imagenes, llm, nlp = nlpOk) {
  const nodos = { Config: [config], 'HTTP Request': imagenes, Resumen_GRU: [gru], Lectura_NLP: [], Clasificar_NLP_Python: nlp ? [nlp] : [] };
  const integ = ejecutar('integracion_3_modelos.js', [{}], nodos);
  if (!integ.length) return { integ };
  nodos.Integracion_3_Modelos = integ;
  const val = ejecutar('validacion_seguridad_final.js', [llm], nodos);
  const reg = ejecutar('preparar_registro_integrado.js', val, nodos);
  return { integ: integ[0], val: val[0], reg };
}

caso('1 Pieza defectuosa + LLM valido', () => {
  const r = cadena([img('VG_T1.jpeg', 'Defectuosa', 0.9963, false)], llmResp(base));
  return { ok: r.val.fuente_analisis === 'LLM_VALIDADO' && r.reg[0].prioridad === 'alta' && r.reg[0].tiene_alertas &&
    r.integ.alertas.some(a => a.tipo === 'INCONSISTENCIA_API') && !r.val.controles_seguridad.alucinacion_sospechada,
    detalle: { fuente: r.val.fuente_analisis, alertas: r.integ.alertas.map(a => a.tipo), clave: r.reg[0].clave_unica } };
});
caso('2 Pieza correcta alta confianza, LLM pone prioridad baja (permitido)', () => {
  const r = cadena([img('VG_T2.jpeg', 'Correcta', 0.9953, false)], llmResp({ ...base, prioridad: 'baja',
    diagnostico: 'ResNet18 clasifico VG_T2.jpeg como Correcta con 99.53 %.' }));
  return { ok: r.val.prioridad === 'baja' && r.val.requiere_revision_humana === true && r.reg[0].aprobacion_automatica === false,
    detalle: { prioridad: r.val.prioridad, fuente: r.val.fuente_analisis } };
});
caso('3 LLM intenta aprobar automaticamente y baja prioridad con defecto -> corregido', () => {
  const r = cadena([img('VG_T3.jpeg', 'Defectuosa', 0.96, false)], llmResp({ ...base, prioridad: 'baja', aprobacion_automatica: true, requiere_revision_humana: false }));
  return { ok: r.val.fuente_analisis === 'LLM_CORREGIDO' && r.val.prioridad === 'alta' && r.val.aprobacion_automatica === false,
    detalle: r.val.controles_seguridad.correcciones_aplicadas };
});
caso('4 JSON invalido del LLM -> respaldo determinista', () => {
  const r = cadena([img('VG_T4.jpeg', 'Defectuosa', 0.97, false)], llmResp('{"diagnostico": "texto cortado'));
  return { ok: r.val.fuente_analisis === 'RESPALDO_DETERMINISTA' && r.val.prioridad === 'alta' && r.reg.length === 1,
    detalle: { fallas: r.val.controles_seguridad.fallas_llm, diag: r.val.diagnostico.slice(0, 120) } };
});
caso('5 Nodo LLM con error tras reintentos -> respaldo', () => {
  const r = cadena([img('VG_T5.jpeg', 'Correcta', 0.72, true)], { error: { message: '429 rate limit' } });
  return { ok: r.val.fuente_analisis === 'RESPALDO_DETERMINISTA' && r.integ.alertas.some(a => a.tipo === 'CONFIANZA_BAJA'),
    detalle: r.val.controles_seguridad.fallas_llm };
});
caso('6 Alucinacion numerica: cifra inventada', () => {
  const r = cadena([img('VG_T6.jpeg', 'Defectuosa', 0.9963, false)], llmResp({ ...base,
    diagnostico: 'Defectuosa con 99.63 %; el lote tiene 37 % de porosidad y se perderan 1250 dolares.' }));
  const cs = r.val.controles_seguridad;
  return { ok: cs.alucinacion_sospechada && cs.cifras_no_respaldadas.includes('37') && cs.cifras_no_respaldadas.includes('1250') && r.reg[0].alucinacion_sospechada,
    detalle: cs.cifras_no_respaldadas };
});
caso('7 Frase de aprobacion sin negacion', () => {
  const r = cadena([img('VG_T7.jpeg', 'Correcta', 0.99, false)], llmResp({ ...base, prioridad: 'baja', recomendacion: 'La pieza queda aprobada para despacho.' }));
  return { ok: r.val.controles_seguridad.frases_aprobacion_sospechosas.length === 1, detalle: r.val.controles_seguridad.frases_aprobacion_sospechosas };
});
caso('8 Sin imagenes validas -> Integracion devuelve 0 items (sin error)', () => {
  const r = cadena([], llmResp(base));
  return { ok: Array.isArray(r.integ) && r.integ.length === 0, detalle: 'items=0' };
});
caso('9 Imagen corrupta (error API) + otra valida', () => {
  const r = cadena([{ error: { message: '400 Archivo de imagen no valido' } }, img('VG_T9.jpeg', 'Correcta', 0.98, false)], llmResp({ ...base, prioridad: 'media' }));
  return { ok: r.reg.length === 1 && r.integ.alertas.some(a => a.tipo === 'ERROR_INFERENCIA_IMAGEN'), detalle: r.integ.alertas.map(a => a.tipo) };
});
caso('10 NLP no disponible -> alerta y flujo sigue', () => {
  const r = cadena([img('VG_T10.jpeg', 'Defectuosa', 0.99, false)], llmResp(base), null);
  return { ok: r.integ.alertas.some(a => a.tipo === 'NLP_TRANSFORMER_NO_DISPONIBLE') && r.reg[0].nlp_transformer_ejecutado === false,
    detalle: r.reg[0].nlp_causa_principal };
});
caso('11 Dos imagenes -> dos filas con claves distintas y alertas por imagen', () => {
  const r = cadena([img('A.jpeg', 'Defectuosa', 0.99, false), img('B.jpeg', 'Correcta', 0.99, false)], llmResp(base));
  const [a, b] = r.reg;
  return { ok: a.clave_unica !== b.clave_unica && a.alertas.includes('A.jpeg') && !b.alertas.includes('A.jpeg'),
    detalle: [a.clave_unica, b.clave_unica, b.alertas] };
});
caso('12 Respuesta envuelta en ```json``` se acepta', () => {
  const r = cadena([img('VG_T12.jpeg', 'Defectuosa', 0.99, false)], llmResp('```json\n' + JSON.stringify(base) + '\n```'));
  return { ok: r.val.fuente_analisis === 'LLM_VALIDADO', detalle: r.val.fuente_analisis };
});

// ----- NLP: Preparar -> Parsear con embeddings sinteticos (bolsa de palabras) -> respaldo JS
const csv = fs.readFileSync(path.join(__dirname, '..', 'python', 'nlp', 'reportes_nc_simulados.csv'), 'utf8').trim().split(/\r?\n/);
const cab = csv[0].split(',');
const filas = csv.slice(1).map(l => { const m = l.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map(s => s.replace(/,$/, '').replace(/^"|"$/g, '')); return Object.fromEntries(cab.map((c, i) => [c, m[i]])); });
filas.push({ id_reporte: '', texto_reporte: 'fila vacia' }, { ...filas[0] });   // invalida + duplicada
const prep = ejecutar('preparar_textos_nlp.js', filas, {});
const vocab = [...new Set(prep[0].reportes.flatMap(r => r.texto.toLowerCase().split(/\W+/)))];
const bow = t => { const s = t.toLowerCase().split(/\W+/); return vocab.map(v => s.filter(x => x === v).length); };
const unido = { ...prep[0], respuesta_hf: JSON.stringify(prep[0].reportes.map(r => bow(r.texto))) };
const pars = ejecutar('parsear_embeddings.js', [unido], {});
const nlpJs = ejecutar('clasificar_nlp_respaldo.js', pars, {});
const parsMal = ejecutar('parsear_embeddings.js', [{ ...prep[0], error: { message: '401 Unauthorized' } }], {});
const nlpSinTf = ejecutar('clasificar_nlp_respaldo.js', parsMal, {});
caso('13 Preparar NLP descarta fila vacia y duplicado', () => ({ ok: prep[0].total === 110 && prep[0].descartados.length === 2, detalle: prep[0].descartados }));
caso('14 NLP JS con embeddings sinteticos produce metricas', () => ({ ok: nlpJs[0].transformer_ejecutado && nlpJs[0].metricas_prueba.reglas.accuracy === 0.425,
  detalle: nlpJs[0].metricas_prueba }));
caso('15 NLP sin token HF -> solo reglas', () => ({ ok: nlpSinTf[0].transformer_ejecutado === false && nlpSinTf[0].motivo_sin_transformer.includes('401'),
  detalle: nlpSinTf[0].motivo_sin_transformer }));
fs.writeFileSync(path.join(__dirname, 'entrada_python_nlp.json'), JSON.stringify(pars[0]));
fs.writeFileSync(path.join(__dirname, 'salida_js_nlp.json'), JSON.stringify(nlpJs[0]));

fs.writeFileSync(path.join(__dirname, 'resultados_pruebas_nodos.json'), JSON.stringify(resultados, null, 2));
for (const r of resultados) console.log((r.ok ? 'OK   ' : 'FALLA') + ' ' + r.caso + ' :: ' + JSON.stringify(r.detalle).slice(0, 160));
console.log(`\n${resultados.filter(r => r.ok).length}/${resultados.length} pruebas OK`);
