/*
 VISIONGUARD INDUSTRIAL v2.2 - INTEGRACION DE 3 MODELOS (nodo Code JS)
 ResNet18 (imagen) + GRU (serie temporal) + Transformer NLP (texto)
 Construye el RESUMEN ESTRUCTURADO que recibe el LLM (nunca la tabla cruda)
 y calcula las alertas condicionales con los umbrales de Config.
*/
const cfg = $('Config').first().json;

// Lee un nodo sin romper si no se ejecuto en esta corrida (p. ej. sin imagenes).
function leer(nodo) {
  try { return $(nodo).all().map(i => i.json); } catch (e) { return []; }
}
const esVerdadero = v => v === true || String(v ?? '').trim().toLowerCase() === 'true';
const esFalso = v => v === false || String(v ?? '').trim().toLowerCase() === 'false';

const datosResNet = leer('HTTP Request');
const imagenes = datosResNet.filter(d =>
  ['correcta', 'defectuosa'].includes(String(d.clasificacion ?? '').trim().toLowerCase()));
const erroresInferencia = datosResNet.length - imagenes.length;

// Sin imagenes validas: la rama Hay_Imagenes_Pendientes ya envio el aviso del turno.
if (imagenes.length === 0) return [];

const gru = leer('Resumen_GRU').find(d => d.tipo === 'RESUMEN_GRU');
if (!gru) throw new Error('Integracion incompleta: falta el resumen GRU (API de series).');

const nlpTf = leer('Clasificar_NLP_Python')[0] || leer('Clasificar_NLP_JS_respaldo')[0] || null;
const nlpHistorico = leer('Lectura_NLP').filter(d => d.id_caso && String(d.modulo ?? '').trim() === 'Transformer_NLP');

const umbralConf = Number(cfg.umbral_confianza ?? 0.9);
const umbralPron = Number(cfg.umbral_pronostico_pct ?? 7.5);
const umbralDisc = Number(cfg.umbral_discrepancia_pp ?? 1.5);

// 1. ResNet18 con regla de seguridad: defectuosa => revision humana
const resultadosImagenes = imagenes.map(d => {
  const clasificacion = String(d.clasificacion).trim();
  const esDefectuosa = clasificacion.toLowerCase() === 'defectuosa';
  return {
    archivo: d.archivo,
    modelo: d.modelo ?? 'ResNet18',
    clasificacion,
    confianza: Number(d.confianza),
    probabilidad_defecto: Number(d.probabilidades?.defectuosa),
    decision_sugerida: d.decision_sugerida,
    requiere_revision_humana_reportada: d.requiere_revision_humana,
    requiere_revision_humana: esDefectuosa || esVerdadero(d.requiere_revision_humana),
    aprobacion_automatica: false
  };
});

// 2. Alertas condicionales (cada una con su regla explicita)
const alertas = [];
for (const im of resultadosImagenes) {
  if (im.clasificacion.toLowerCase() === 'defectuosa')
    alertas.push({ tipo: 'PIEZA_DEFECTUOSA', detalle: `${im.archivo} clasificada Defectuosa` });
  if (Number.isFinite(im.confianza) && im.confianza < umbralConf)
    alertas.push({ tipo: 'CONFIANZA_BAJA', detalle: `${im.archivo}: confianza ${(im.confianza * 100).toFixed(2)} % < ${umbralConf * 100} %` });
  if (im.clasificacion.toLowerCase() === 'defectuosa' && esFalso(im.requiere_revision_humana_reportada))
    alertas.push({ tipo: 'INCONSISTENCIA_API', detalle: `${im.archivo}: defectuosa sin revision exigida por la API; se fuerza revision humana` });
}
for (const p of gru.pronosticos ?? []) {
  if (Number(p.gru_pct) >= umbralPron)
    alertas.push({ tipo: 'PRONOSTICO_SOBRE_UMBRAL', detalle: `Linea ${p.linea}: GRU ${p.gru_pct} % >= ${umbralPron} % (simulado)` });
  if (Math.abs(Number(p.gru_pct) - Number(p.promedio_movil_pct)) >= umbralDisc)
    alertas.push({ tipo: 'DISCREPANCIA_MODELOS_SERIE', detalle: `Linea ${p.linea}: GRU ${p.gru_pct} % vs promedio movil ${p.promedio_movil_pct} %` });
}
if (erroresInferencia > 0)
  alertas.push({ tipo: 'ERROR_INFERENCIA_IMAGEN', detalle: `${erroresInferencia} imagen(es) sin resultado valido de la API` });
if (!nlpTf || nlpTf.transformer_ejecutado !== true)
  alertas.push({ tipo: 'NLP_TRANSFORMER_NO_DISPONIBLE', detalle: nlpTf?.motivo_sin_transformer || 'Sin resultado NLP; solo reglas o sin datos' });

// 3. Resumen NLP compacto (resultados, no textos crudos)
const nlp = nlpTf ? {
  transformer_ejecutado: nlpTf.transformer_ejecutado,
  modelo: nlpTf.modelo,
  metodo: nlpTf.metodo,
  metricas_prueba: nlpTf.metricas_prueba,
  mejor_metodo_en_prueba_f1: nlpTf.mejor_metodo_en_prueba_f1,
  metodo_usado_operacion: nlpTf.metodo_usado_operacion,
  n_operacion: nlpTf.n_operacion,
  distribucion_causas_operacion: nlpTf.distribucion_causas_operacion,
  causa_principal_operacion: nlpTf.causa_principal_operacion,
  concordancia_transformer_reglas_pct: nlpTf.concordancia_transformer_reglas_pct,
  casos_operacion: (nlpTf.casos_operacion || []).slice(0, 5)
} : { transformer_ejecutado: false, causa_principal_operacion: 'sin_datos' };

return [{
  json: {
    sistema: 'VisionGuard Industrial',
    tipo: 'ANALISIS_INTEGRADO',
    origen: 'PROTOTIPO_ACADEMICO_CON_DATOS_SIMULADOS',
    modelos_integrados: ['ResNet18', 'GRU', 'Transformer_NLP'],
    resumen_integracion: {
      total_imagenes: resultadosImagenes.length,
      total_defectuosas: resultadosImagenes.filter(d => d.clasificacion.toLowerCase() === 'defectuosa').length,
      total_lineas: gru.total_lineas,
      linea_mayor_pronostico: gru.linea_mayor_pronostico,
      mayor_pronostico_pct: gru.mayor_pronostico_pct,
      total_casos_nlp: nlpHistorico.length,
      total_alertas: alertas.length
    },
    imagenes: resultadosImagenes,
    series_temporales: gru,
    nlp_transformer: nlp,
    analisis_nlp: nlpHistorico.slice(0, 5).map(d => ({
      id_caso: d.id_caso, recomendacion: d.recomendacion_original,
      accion_sugerida: d.accion_sugerida, estado: d.estado
    })),
    alertas,
    umbrales: { confianza: umbralConf, pronostico_pct: umbralPron, discrepancia_pp: umbralDisc },
    advertencias: [
      'Los datos GRU y los reportes NC son simulados con fines academicos.',
      'Los pronosticos GRU no son mediciones en tiempo real.',
      'Los reportes NC no necesariamente corresponden a las imagenes analizadas.',
      'Una clasificacion Correcta no constituye aprobacion definitiva.',
      'Toda pieza defectuosa requiere revision humana.',
      'Ninguna pieza puede aprobarse automaticamente.'
    ],
    requiere_validacion_humana: true,
    aprobacion_automatica: false,
    estado: 'PENDIENTE_VALIDACION_HUMANA'
  }
}];
