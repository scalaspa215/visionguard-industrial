/**
 * VISIONGUARD INDUSTRIAL v2.2 - TABLERO INTERACTIVO EN GOOGLE SHEETS
 *
 * Instalar (una vez):
 *   1. Abrir VisionGuard_Historial_Inspecciones > Extensiones > Apps Script.
 *   2. Pegar este archivo completo, guardar y ejecutar `instalarVisionGuard`.
 *      (Google pedira autorizar el script sobre ESTA hoja; no usa claves.)
 *   3. Copiar la URL que aparece en Dashboard!B2 en el nodo Config del flujo
 *      n8n (campo dashboard_url).
 *   4. Compartir la hoja con el profesor como LECTOR (Compartir > Lector).
 *
 * Que crea:
 *   - Reportes_NC        : 110 reportes NC SIMULADOS (si la pestana no existe).
 *   - Dashboard          : KPIs, filtros (clasificacion, prioridad, fecha desde),
 *                          9 graficos, registro de recomendaciones del LLM y
 *                          evidencia de modelos/ROI.
 *   - Dashboard_datos    : tabla auxiliar filtrada (no editar).
 * Los filtros son listas desplegables: al cambiarlas, KPIs, graficos y tablas
 * se recalculan solos. Menu "VisionGuard > Reconstruir tablero" para rehacerlo.
 */

const VG = {
  HOJA: 'Analisis_Integrado',
  GRU: 'Pronosticos_GRU',
  NC: 'Reportes_NC',
  DASH: 'Dashboard',
  AUX: 'Dashboard_datos',
  AZUL: '#17283f', ACENTO: '#3557bd', CORAL: '#d6605d', VERDE: '#258c7a', NARANJA: '#d9864c', FONDO: '#f4f7fb'
};

// Evidencia offline (archivos resultados_*.json del repositorio). Fuente indicada en el tablero.
const EVIDENCIA = __EVIDENCIA__;
const REPORTES_NC = __REPORTES_NC__;

function onOpen() {
  SpreadsheetApp.getUi().createMenu('VisionGuard')
    .addItem('Reconstruir tablero', 'construirDashboard')
    .addItem('Verificar permisos de la hoja', 'verificarPermisos')
    .addToUi();
}

function instalarVisionGuard() {
  crearReportesNC_();
  construirDashboard();
}

function crearReportesNC_() {
  const ss = SpreadsheetApp.getActive();
  if (ss.getSheetByName(VG.NC)) return;
  const sh = ss.insertSheet(VG.NC);
  sh.getRange(1, 1, REPORTES_NC.length, REPORTES_NC[0].length).setValues(REPORTES_NC);
  sh.setFrozenRows(1);
  sh.getRange('1:1').setFontWeight('bold').setBackground('#e9f0ff');
  sh.autoResizeColumns(1, 6);
}

/** Letra de columna de un encabezado; null si no existe todavia. */
function letra_(sh, nombre) {
  const cab = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(h => String(h).trim());
  const i = cab.indexOf(nombre);
  if (i < 0) return null;
  let n = i + 1, s = '';
  while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}

function construirDashboard() {
  const ss = SpreadsheetApp.getActive();
  const datos = ss.getSheetByName(VG.HOJA);
  if (!datos) throw new Error('No existe la pestana ' + VG.HOJA);
  const H = "'" + VG.HOJA + "'!";
  const col = nombre => letra_(datos, nombre);
  const rango = nombre => {
    const c = col(nombre);
    return c ? `${H}${c}2:${c}` : `IF(LEN(${H}${col('archivo')}2:${col('archivo')}),"n/d","")`;
  };
  ['archivo', 'clasificacion', 'confianza', 'prioridad', 'fecha_registro', 'estado'].forEach(c => {
    if (!col(c)) throw new Error('Falta la columna obligatoria: ' + c);
  });

  // ---------- hojas limpias
  let dash = ss.getSheetByName(VG.DASH);
  if (dash) { dash.getCharts().forEach(ch => dash.removeChart(ch)); dash.clear(); dash.clearConditionalFormatRules(); }
  else dash = ss.insertSheet(VG.DASH, 0);
  let aux = ss.getSheetByName(VG.AUX);
  if (aux) aux.clear(); else aux = ss.insertSheet(VG.AUX);
  ss.setActiveSheet(dash);
  ss.moveActiveSheet(1);

  // ---------- tabla auxiliar filtrada por los controles del tablero
  const D = "'" + VG.DASH + "'!";
  const fecha = `IFERROR(DATEVALUE(LEFT(TO_TEXT(${rango('fecha_registro')}),10)))`;
  aux.getRange('A1:L1').setValues([['clasificacion', 'prioridad', 'confianza', 'fecha', 'estado', 'archivo',
    'pronostico_max_pct', 'linea', 'fuente_analisis', 'alucinacion', 'decision_humana', 'recomendacion']]);
  aux.getRange('A2').setFormula(
    `=IFERROR(FILTER({${rango('clasificacion')},${rango('prioridad')},${rango('confianza')},${fecha},` +
    `${rango('estado')},${rango('archivo')},${rango('pronostico_max_pct')},${rango('linea_mayor_pronostico')},` +
    `${rango('fuente_analisis')},${rango('alucinacion_sospechada')},${rango('decision_humana')},${rango('recomendacion')}},` +
    `LEN(${rango('archivo')}),` +
    `(${D}$C$5="Todas")+(${rango('clasificacion')}=${D}$C$5),` +
    `(${D}$F$5="Todas")+(${rango('prioridad')}=${D}$F$5),` +
    `${fecha}>=${D}$I$5),"")`);
  aux.getRange('D2:D').setNumberFormat('yyyy-mm-dd');

  // agregados para graficos (columnas N en adelante)
  aux.getRange('N1:O3').setValues([['Clase', 'Piezas'], ['Correcta', ''], ['Defectuosa', '']]);
  aux.getRange('O2').setFormula('=COUNTIF(A2:A,"Correcta")');
  aux.getRange('O3').setFormula('=COUNTIF(A2:A,"Defectuosa")');
  aux.getRange('Q1:R4').setValues([['Prioridad', 'Inspecciones'], ['alta', ''], ['media', ''], ['baja', '']]);
  ['R2', 'R3', 'R4'].forEach((c, i) => aux.getRange(c).setFormula(`=COUNTIF(B2:B,Q${i + 2})`));
  aux.getRange('T1').setFormula('=IFERROR(QUERY(A2:F,"select D, count(F) where F<>\'\' group by D pivot A label D \'Fecha\'",0),"")');
  aux.getRange('Z1').setFormula('=IFERROR(QUERY(A2:F,"select D, avg(C) where F<>\'\' group by D label D \'Fecha\', avg(C) \'Confianza media\'",0),"")');
  aux.getRange('AC1').setFormula('=IFERROR(QUERY(E2:F,"select E, count(F) where F<>\'\' group by E label E \'Estado\', count(F) \'Inspecciones\'",0),"")');

  // historial GRU (todas las ejecuciones registradas)
  const gru = ss.getSheetByName(VG.GRU);
  if (gru) {
    const G = "'" + VG.GRU + "'!";
    const cf = letra_(gru, 'fecha_registro'), cl = letra_(gru, 'linea'), cg = letra_(gru, 'pronostico_gru_pct'),
      cm = letra_(gru, 'pronostico_promedio_movil_pct');
    if (cf && cl && cg) {
      aux.getRange('AF1').setFormula(`=IFERROR(QUERY(ARRAYFORMULA({IFERROR(DATEVALUE(LEFT(TO_TEXT(${G}${cf}2:${cf}),10))),${G}${cl}2:${cl},${G}${cg}2:${cg}}),` +
        `"select Col1, avg(Col3) where Col2 is not null group by Col1 pivot Col2 label Col1 'Fecha'",0),"")`);
      aux.getRange('AF2:AF').setNumberFormat('yyyy-mm-dd');
    }
    if (cl && cg && cm) {
      aux.getRange('AL1').setFormula(`=IFERROR(QUERY({${G}${cl}2:${cl},${G}${cg}2:${cg},${G}${cm}2:${cm}},` +
        `"select Col1, avg(Col2), avg(Col3) where Col1 is not null group by Col1 label Col1 'Linea', avg(Col2) 'GRU %', avg(Col3) 'Promedio movil %'",0),"")`);
    }
  }
  // evidencia offline
  const ev = (fila, columna, valores) => aux.getRange(fila, columna, valores.length, valores[0].length).setValues(valores);
  ev(1, 40, EVIDENCIA.series);   // AN
  ev(1, 44, EVIDENCIA.nlp);      // AR
  ev(1, 48, EVIDENCIA.roi);      // AV
  aux.hideSheet();

  // ---------- encabezado
  dash.setHiddenGridlines(true);
  dash.setColumnWidth(1, 16);
  for (let c = 2; c <= 13; c++) dash.setColumnWidth(c, 118);
  dash.getRange('B1:M1').merge().setValue('🛡️ VisionGuard Industrial · Centro de control (Hito 2)')
    .setFontSize(20).setFontWeight('bold').setFontColor('#ffffff').setBackground(VG.AZUL).setVerticalAlignment('middle');
  dash.setRowHeight(1, 46);
  const url = ss.getUrl() + '#gid=' + dash.getSheetId();
  dash.getRange('B2:M2').merge().setValue(url).setFontColor('#ffffff').setBackground('#28517a').setFontSize(9);
  dash.getRange('B3:M3').merge()
    .setValue('ResNet18 (imagen) · GRU (serie temporal) · Transformer NLP (texto) · GPT-4o mini · supervisión humana. ' +
      'Prototipo académico: GRU y reportes NC son SIMULADOS; ninguna pieza se aprueba automáticamente.')
    .setFontColor('#5d6f89').setWrap(true);

  // ---------- controles interactivos
  const lista = (celda, valores) => dash.getRange(celda).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(valores, true).setAllowInvalid(false).build()).setValue(valores[0]);
  dash.getRange('B5').setValue('Clasificación ▸').setFontWeight('bold');
  lista('C5', ['Todas', 'Correcta', 'Defectuosa']);
  dash.getRange('E5').setValue('Prioridad ▸').setFontWeight('bold');
  lista('F5', ['Todas', 'alta', 'media', 'baja']);
  dash.getRange('H5').setValue('Desde ▸').setFontWeight('bold');
  dash.getRange('I5').setValue(new Date(2026, 10, 1)).setNumberFormat('yyyy-mm-dd')
    .setDataValidation(SpreadsheetApp.newDataValidation().requireDate().build());
  dash.getRange('K5:M5').merge().setValue('Cambie los filtros: todo se recalcula.').setFontColor('#61738b').setFontStyle('italic');
  dash.getRange('C5:C5').setBackground('#e9f0ff');
  dash.getRange('F5:F5').setBackground('#e9f0ff');
  dash.getRange('I5:I5').setBackground('#e9f0ff');

  // ---------- KPIs
  const A = "'" + VG.AUX + "'!";
  const kpis = [
    ['Inspecciones', `=COUNTA(${A}F2:F)`, '0'],
    ['Defectuosas', `=COUNTIF(${A}A2:A,"Defectuosa")`, '0'],
    ['Tasa de defectos', `=IFERROR(COUNTIF(${A}A2:A,"Defectuosa")/COUNTA(${A}F2:F),0)`, '0.0%'],
    ['Confianza media', `=IFERROR(AVERAGE(${A}C2:C),"—")`, '0.00%'],
    ['Pendientes', `=COUNTIF(${A}E2:E,"PENDIENTE_VALIDACION_HUMANA")`, '0'],
    ['Autorizadas', `=COUNTIF(${A}E2:E,"ACCION_AUTORIZADA_POR_HUMANO")`, '0'],
    ['Rechazadas', `=COUNTIF(${A}E2:E,"ACCION_RECHAZADA_POR_HUMANO")`, '0'],
    ['Sin respuesta', `=COUNTIF(${A}E2:E,"SIN_RESPUESTA_HUMANA_ESCALAR")`, '0'],
    ['Respaldo determinista', `=COUNTIF(${A}I2:I,"RESPALDO_DETERMINISTA")`, '0'],
    ['Cifras no respaldadas', `=SUMPRODUCT(--REGEXMATCH(LOWER(TO_TEXT(${A}J2:J)),"true"))`, '0'],
    ['ROI base (año 1)', '=0.365', '0.0%'],
    ['Recuperación base', `="${EVIDENCIA.recuperacion_base} meses"`, '@'],
  ];
  kpis.forEach(([t, f, fmt], i) => {
    const c = 2 + i;
    dash.getRange(7, c).setValue(t).setFontSize(9).setFontColor('#566d89').setWrap(true).setFontWeight('bold');
    dash.getRange(8, c).setFormula(f).setNumberFormat(fmt).setFontSize(18).setFontWeight('bold').setFontColor(i === 1 || i === 2 ? VG.CORAL : VG.AZUL);
  });
  dash.getRange('B7:M8').setBackground('#ffffff').setBorder(true, true, true, true, true, false, '#dce5f1', SpreadsheetApp.BorderStyle.SOLID);
  dash.setRowHeight(7, 34);
  dash.setRowHeight(8, 40);

  // ---------- graficos
  const grafico = (tipo, rangos, fila, columna, titulo, opciones = {}) => {
    let b = dash.newChart().setChartType(tipo).setPosition(fila, columna, 0, 0).setOption('title', titulo)
      .setOption('width', 470).setOption('height', 270).setOption('legend', { position: 'bottom' })
      .setOption('titleTextStyle', { color: VG.AZUL, fontSize: 13, bold: true });
    rangos.forEach(r => { b = b.addRange(aux.getRange(r)); });
    Object.entries(opciones).forEach(([k, v]) => { b = b.setOption(k, v); });
    dash.insertChart(b.build());
  };
  const C = Charts.ChartType;
  grafico(C.PIE, ['N1:O3'], 10, 2, '1 · Clasificación ResNet18 (filtrada)', { pieHole: 0.55, colors: [VG.VERDE, VG.CORAL] });
  grafico(C.COLUMN, ['Q1:R4'], 10, 6, '2 · Prioridad asignada', { colors: [VG.NARANJA], legend: { position: 'none' } });
  grafico(C.COLUMN, ['T1:W60'], 10, 10, '3 · Inspecciones por día y clase', { isStacked: true, colors: [VG.VERDE, VG.CORAL] });
  grafico(C.LINE, ['Z1:AA60'], 24, 2, '4 · Confianza media ResNet18 en el tiempo', { colors: [VG.ACENTO], vAxis: { format: 'percent' }, pointSize: 5 });
  grafico(C.BAR, ['AC1:AD8'], 24, 6, '5 · Decisiones humanas (estado)', { colors: [VG.VERDE], legend: { position: 'none' } });
  if (gru) grafico(C.LINE, ['AF1:AI60'], 24, 10, '6 · GRU: pronóstico por línea en el tiempo (simulado)', { pointSize: 5 });
  grafico(C.COLUMN, ['AN1:AP8'], 38, 2, '7 · Series: MAE (pp) validación vs prueba', { colors: ['#9fb3e6', VG.ACENTO] });
  grafico(C.COLUMN, ['AR1:AT3'], 38, 6, '8 · NLP: Transformer vs reglas (prueba)', { colors: ['#9fb3e6', VG.ACENTO] });
  grafico(C.COLUMN, ['AV1:AW4'], 38, 10, '9 · ROI año 1 por escenario (estimado)', { colors: [VG.ACENTO], legend: { position: 'none' } });

  // ---------- registro de recomendaciones del LLM
  dash.getRange('B52').setValue('Registro de recomendaciones (últimas 15, según filtros)').setFontWeight('bold').setFontSize(13).setFontColor(VG.AZUL);
  dash.getRange('B53').setFormula(`=IFERROR(QUERY(${A}A2:L,"select D, F, A, B, E, I, L where F<>'' order by D desc limit 15 label D 'Fecha', F 'Archivo', A 'Clase', B 'Prioridad', E 'Estado', I 'Fuente', L 'Recomendación'",0),"Sin registros")`);
  dash.getRange('B54:B70').setNumberFormat('yyyy-mm-dd');
  dash.getRange('H53:M70').setWrap(true);

  // ---------- evidencia ResNet18 (Hito 1, test independiente)
  dash.getRange('B73').setValue('Evidencia de modelos (conjuntos de prueba no usados para entrenar)').setFontWeight('bold').setFontSize(13).setFontColor(VG.AZUL);
  dash.getRange(74, 2, EVIDENCIA.resnet.length, EVIDENCIA.resnet[0].length).setValues(EVIDENCIA.resnet);
  dash.getRange(74, 7, EVIDENCIA.series_tabla.length, EVIDENCIA.series_tabla[0].length).setValues(EVIDENCIA.series_tabla);
  dash.getRange('B74:E74').setFontWeight('bold').setBackground('#e9f0ff');
  dash.getRange('G74:J74').setFontWeight('bold').setBackground('#e9f0ff');
  dash.getRange(75 + EVIDENCIA.series_tabla.length, 2).setValue(EVIDENCIA.nota).setFontColor('#61738b').setWrap(false);

  SpreadsheetApp.flush();
  Logger.log('Tablero listo: ' + url);
  try { SpreadsheetApp.getUi().alert('Tablero VisionGuard listo.\n\nURL para Config.dashboard_url:\n' + url); } catch (e) { /* ejecucion sin UI */ }
}

/** Solo informa el estado de comparticion; no modifica permisos. */
function verificarPermisos() {
  const f = DriveApp.getFileById(SpreadsheetApp.getActive().getId());
  const msg = `Acceso general: ${f.getSharingAccess()} · Permiso: ${f.getSharingPermission()}\n` +
    `Lectores: ${f.getViewers().length} · Editores: ${f.getEditors().length}\n` +
    'Para el profesor: Compartir > agregar su correo como Lector (no Editor).';
  Logger.log(msg);
  try { SpreadsheetApp.getUi().alert(msg); } catch (e) { /* sin UI */ }
}
