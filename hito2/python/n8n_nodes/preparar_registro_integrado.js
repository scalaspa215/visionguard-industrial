/*
 VISIONGUARD INDUSTRIAL v2.2 - PREPARAR REGISTRO INTEGRADO (nodo Code JS)
 Una fila por imagen para la pestana Analisis_Integrado.
 clave_unica = INTEGRADO|archivo|fecha_de_ejecucion -> la misma imagen no se
 registra ni se notifica dos veces el mismo dia (ver Evitar_Notificaciones_Duplicadas).
 Las columnas nuevas (v2.2) se agregan solas en Sheets.
*/
const analisis = $input.first().json;
const integracion = $('Integracion_3_Modelos').first().json;

if (analisis.tipo !== 'ANALISIS_INTEGRADO_VALIDADO') throw new Error('El analisis no ha sido validado.');
if (analisis.requiere_revision_humana !== true || analisis.aprobacion_automatica !== false ||
    analisis.controles_seguridad?.validacion_humana_realizada !== false) {
  throw new Error('Validacion de seguridad incorrecta.');
}

const imagenes = integracion.imagenes ?? [];
if (imagenes.length === 0) throw new Error('No se encontraron imagenes.');
const series = integracion.series_temporales ?? {};
if (!(series.pronosticos ?? []).length) throw new Error('No se encontraron pronosticos GRU.');
const nlp = integracion.nlp_transformer ?? {};
const ahora = $now.setZone('America/Santiago');
const alertas = integracion.alertas ?? [];

return imagenes.map(imagen => {
  const archivo = String(imagen.archivo ?? '').trim();
  if (!archivo) throw new Error('Imagen sin nombre de archivo.');
  // Alertas propias de otra imagen se excluyen; las globales (GRU, NLP) se incluyen siempre.
  const POR_IMAGEN = ['PIEZA_DEFECTUOSA', 'CONFIANZA_BAJA', 'INCONSISTENCIA_API'];
  const alertasImagen = alertas.filter(x => !POR_IMAGEN.includes(x.tipo) || String(x.detalle).includes(archivo));
  return {
    json: {
      clave_unica: ['INTEGRADO', archivo, ahora.toFormat('yyyy-MM-dd')].join('|'),
      fecha_registro: ahora.toFormat('yyyy-MM-dd HH:mm:ss'),
      archivo,
      clasificacion: imagen.clasificacion,
      confianza: Number(imagen.confianza),
      linea_mayor_pronostico: series.linea_mayor_pronostico,
      pronostico_max_pct: Number(series.mayor_pronostico_pct),
      casos_nlp: Number(integracion.resumen_integracion?.total_casos_nlp ?? 0),
      prioridad: analisis.prioridad,
      diagnostico: analisis.diagnostico,
      recomendacion: analisis.recomendacion,
      requiere_revision_humana: true,
      aprobacion_automatica: false,
      estado: 'PENDIENTE_VALIDACION_HUMANA',
      origen: 'PROTOTIPO_ACADEMICO_CON_DATOS_SIMULADOS',
      validacion_humana_realizada: false,
      // --- columnas nuevas v2.2 ---
      probabilidad_defecto: Number(imagen.probabilidad_defecto),
      fuente_analisis: analisis.fuente_analisis,
      alucinacion_sospechada: analisis.controles_seguridad?.alucinacion_sospechada === true,
      tiene_alertas: alertasImagen.length > 0,
      alertas: alertasImagen.map(x => `${x.tipo}: ${x.detalle}`).join(' | '),
      nlp_transformer_ejecutado: nlp.transformer_ejecutado === true,
      nlp_causa_principal: nlp.causa_principal_operacion ?? 'sin_datos',
      nlp_f1_transformer: nlp.metricas_prueba?.transformer?.f1_macro ?? '',
      nlp_f1_reglas: nlp.metricas_prueba?.reglas?.f1_macro ?? '',
      decision_humana: 'PENDIENTE',
      fecha_decision_humana: ''
    }
  };
});
