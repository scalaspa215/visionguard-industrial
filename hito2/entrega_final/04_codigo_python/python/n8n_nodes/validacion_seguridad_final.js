/*
 VISIONGUARD INDUSTRIAL v2.2 - VALIDACION FINAL DE SEGURIDAD (nodo Code JS)

 Capas de control sobre la salida de GPT-4o mini:
  1. Parseo robusto del JSON (tolera ```json ... ```).
  2. Estructura: 11 campos obligatorios y textos no vacios.
  3. Reglas de seguridad deterministas: nunca aprobacion automatica, revision
     humana siempre, prioridad alta si hay pieza defectuosa, origen academico.
     Si el LLM las viola, se CORRIGEN al valor conservador y se registra.
  4. Anti-alucinacion numerica: toda cifra del texto del LLM debe existir en
     los datos de entrada (con tolerancia de redondeo y conversion a %).
  5. Frases de aprobacion sospechosas ("pieza aprobada" sin negacion).
 Si el JSON es inutilizable (o el nodo LLM fallo tras 3 reintentos) se genera
 un ANALISIS DETERMINISTA DE RESPALDO: el flujo no se cae en silencio y el
 correo indica la fuente del analisis.
*/
const ORIGEN = 'PROTOTIPO_ACADEMICO_CON_DATOS_SIMULADOS';
const CAMPOS = ['diagnostico', 'recomendacion', 'prioridad', 'justificacion', 'resumen_imagenes',
  'resumen_series_temporales', 'resumen_nlp', 'riesgos_limitaciones', 'requiere_revision_humana',
  'aprobacion_automatica', 'origen'];
const TEXTOS = ['diagnostico', 'recomendacion', 'justificacion', 'resumen_imagenes',
  'resumen_series_temporales', 'resumen_nlp', 'riesgos_limitaciones'];

const integracion = $('Integracion_3_Modelos').first().json;
const imagenes = integracion.imagenes ?? [];
if (imagenes.length === 0) throw new Error('No existen resultados ResNet18.');
const hayDefectuosa = imagenes.some(d => String(d.clasificacion ?? '').trim().toLowerCase() === 'defectuosa');
const gru = integracion.series_temporales ?? {};
const nlp = integracion.nlp_transformer ?? {};

const fallas = [];       // impiden usar la respuesta
const correcciones = []; // se corrigieron a valor seguro

// ---------- 1. Extraer y parsear
const r = $input.first().json;
if (r.error) fallas.push('Nodo LLM con error: ' + String(r.error.message ?? r.error).slice(0, 160));
const contenido = r.output?.[0]?.content?.find(c => c.type === 'output_text')?.text
  ?? r.output?.[0]?.content?.[0]?.text ?? r.message?.content ?? r.text ?? null;
let a = null;
if (contenido == null) fallas.push('El LLM no entrego contenido.');
else {
  try {
    a = typeof contenido === 'string'
      ? JSON.parse(contenido.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, ''))
      : contenido;
    if (!a || typeof a !== 'object' || Array.isArray(a)) { fallas.push('La respuesta no es un objeto JSON.'); a = null; }
  } catch (e) { fallas.push('JSON invalido del LLM.'); }
}

// ---------- 2. Estructura
if (a) {
  for (const c of CAMPOS) if (!(c in a)) fallas.push(`Falta el campo: ${c}`);
  for (const c of TEXTOS) if (c in a && (typeof a[c] !== 'string' || !a[c].trim())) fallas.push(`Contenido invalido: ${c}`);
}

// ---------- 3. Reglas de seguridad (corregir, no confiar)
if (a && fallas.length === 0) {
  if (!['alta', 'media', 'baja'].includes(a.prioridad)) { correcciones.push(`prioridad '${a.prioridad}' -> alta`); a.prioridad = 'alta'; }
  if (hayDefectuosa && a.prioridad !== 'alta') { correcciones.push('pieza defectuosa: prioridad -> alta'); a.prioridad = 'alta'; }
  if (a.aprobacion_automatica !== false) { correcciones.push('aprobacion_automatica -> false'); a.aprobacion_automatica = false; }
  if (a.requiere_revision_humana !== true) { correcciones.push('requiere_revision_humana -> true'); a.requiere_revision_humana = true; }
  if (a.origen !== ORIGEN) { correcciones.push('origen corregido'); a.origen = ORIGEN; }
  for (const k of Object.keys(a)) if (!CAMPOS.includes(k)) { delete a[k]; correcciones.push(`clave extra eliminada: ${k}`); }
}

// ---------- 4. Anti-alucinacion numerica
const permitidos = new Set();
const agregar = v => {
  if (!Number.isFinite(v)) return;
  [v, v * 100, v / 100].forEach(x => { permitidos.add(+x.toFixed(2)); permitidos.add(+x.toFixed(1)); permitidos.add(Math.round(x)); });
};
(function recorrer(o) {
  if (o == null) return;
  if (typeof o === 'number') agregar(o);
  else if (typeof o === 'string') (o.match(/\d+(?:[.,]\d+)?/g) || []).forEach(s => agregar(parseFloat(s.replace(',', '.'))));
  else if (typeof o === 'object') Object.values(o).forEach(recorrer);
})(integracion);
for (let i = 0; i <= 12; i++) permitidos.add(i);   // conteos y ordinales pequenos ("3 lineas", "L1")
permitidos.add(100);

let noRespaldados = [];
let frasesAprobacion = [];
if (a && fallas.length === 0) {
  const texto = TEXTOS.map(c => a[c]).join(' ');
  noRespaldados = [...new Set((texto.match(/\d+(?:[.,]\d+)?/g) || []))]
    .map(s => ({ s, v: parseFloat(s.replace(',', '.')) }))
    .filter(({ v }) => ![...permitidos].some(p => Math.abs(p - v) <= 0.011))
    .map(({ s }) => s);
  frasesAprobacion = (texto.match(/.{0,30}\baprobad[ao]s?\b/gi) || [])
    .filter(f => !/\b(no|nunca|sin|ninguna|ningun)\b|automatic|definitiv/i.test(f));
  if (noRespaldados.length || frasesAprobacion.length) {
    a.riesgos_limitaciones += ' [CONTROL AUTOMATICO: ' +
      (noRespaldados.length ? `cifras sin respaldo en los datos: ${noRespaldados.join(', ')}. ` : '') +
      (frasesAprobacion.length ? 'se detecto una frase de aprobacion sin negacion; NO hay aprobacion automatica. ' : '') +
      'Verificar contra el panel antes de decidir.]';
  }
}

// ---------- 5. Respaldo determinista
const pct = v => Number.isFinite(Number(v)) ? (Number(v) * 100).toFixed(2) + ' %' : 'n/d';
function respaldo() {
  const def = imagenes.filter(d => String(d.clasificacion).toLowerCase() === 'defectuosa');
  return {
    diagnostico: `Analisis de respaldo (sin LLM valido). ResNet18: ${imagenes.length} imagen(es), ${def.length} defectuosa(s): ` +
      imagenes.map(d => `${d.archivo} ${d.clasificacion} (${pct(d.confianza)})`).join('; ') +
      `. GRU simulado: mayor pronostico en ${gru.linea_mayor_pronostico} (${gru.mayor_pronostico_pct} %). ` +
      `NLP: causa principal de NC ${nlp.causa_principal_operacion ?? 'sin datos'}.`,
    recomendacion: def.length
      ? 'Apartar las piezas defectuosas e inspeccionarlas manualmente. No aprobar automaticamente.'
      : 'Continuar con la validacion humana segun protocolo. No aprobar automaticamente.',
    prioridad: 'alta',
    justificacion: 'Regla determinista aplicada porque la salida del LLM no supero la validacion: ' + fallas.join(' | '),
    resumen_imagenes: imagenes.map(d => `${d.archivo}: ${d.clasificacion}, ${pct(d.confianza)}`).join('; '),
    resumen_series_temporales: (gru.pronosticos ?? []).map(p => `${p.linea}: GRU ${p.gru_pct} %, promedio movil ${p.promedio_movil_pct} %`).join('; ') + ' (simulado).',
    resumen_nlp: nlp.transformer_ejecutado ? `Transformer ejecutado; causa principal ${nlp.causa_principal_operacion}.` : 'Transformer no disponible; solo reglas.',
    riesgos_limitaciones: 'Respuesta del LLM descartada por el control automatico; diagnostico generado por reglas fijas.',
    requiere_revision_humana: true, aprobacion_automatica: false, origen: ORIGEN
  };
}

const usarRespaldo = !a || fallas.length > 0;
const analisis = usarRespaldo ? respaldo() : a;
const fuente = usarRespaldo ? 'RESPALDO_DETERMINISTA' : (correcciones.length ? 'LLM_CORREGIDO' : 'LLM_VALIDADO');

return [{
  json: {
    sistema: 'VisionGuard Industrial',
    tipo: 'ANALISIS_INTEGRADO_VALIDADO',
    ...analisis,
    estado: 'PENDIENTE_VALIDACION_HUMANA',
    fuente_analisis: fuente,
    controles_seguridad: {
      json_valido: !usarRespaldo,
      fallas_llm: fallas,
      correcciones_aplicadas: correcciones,
      cifras_no_respaldadas: noRespaldados,
      frases_aprobacion_sospechosas: frasesAprobacion,
      alucinacion_sospechada: noRespaldados.length > 0 || frasesAprobacion.length > 0,
      revision_humana_obligatoria: true,
      aprobacion_automatica_bloqueada: true,
      validacion_humana_realizada: false
    },
    total_imagenes: integracion.resumen_integracion?.total_imagenes,
    total_casos_nlp: integracion.resumen_integracion?.total_casos_nlp
  }
}];
