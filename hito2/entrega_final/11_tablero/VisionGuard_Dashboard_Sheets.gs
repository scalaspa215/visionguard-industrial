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
const EVIDENCIA = {"series": [["Modelo", "MAE validación", "MAE prueba"], ["SES", 1.4867, 1.5666], ["Holt-Winters 7d", 1.4067, 1.5988], ["Promedio movil 7d", 1.5707, 1.6167], ["Regresion lag+semana", 1.4738, 1.7167], ["Holt", 1.6919, 1.7463], ["GRU", 1.5464, 1.7666], ["Ingenuo", 1.7849, 2.0543]], "series_tabla": [["Serie (1 día, pp)", "MAE val", "MAE prueba", "RMSE prueba"], ["SES", 1.4867, 1.5666, 1.9043], ["Holt-Winters 7d", 1.4067, 1.5988, 1.9789], ["Promedio movil 7d", 1.5707, 1.6167, 1.9631], ["Regresion lag+semana", 1.4738, 1.7167, 2.1946], ["Holt", 1.6919, 1.7463, 2.1366], ["GRU", 1.5464, 1.7666, 2.2623], ["Ingenuo", 1.7849, 2.0543, 2.5263]], "nlp": [["Método", "Accuracy", "F1 macro"], ["Reglas fijas", 0.425, 0.5154], ["Transformer (MiniLM)", 0.375, 0.3469]], "roi": [["Escenario", "ROI año 1 (%)"], ["Conservador", 5.5], ["Base", 36.5], ["Optimista", 260.3]], "resnet": [["ResNet18 · test 715 img.", "Umbral simple", "ResNet18", "Fuente"], ["Accuracy", 0.6951, 0.9776, "Colab Hito 1"], ["Precisión defectuosa", 0.7818, 0.9932, "Colab Hito 1"], ["Recall defectuosa", 0.7196, 0.9713, "Colab Hito 1"], ["F1 defectuosa", 0.7494, 0.9821, "Colab Hito 1"], ["Falsos negativos", "—", "13 de 453", "Colab Hito 1"]], "recuperacion_base": 6.7, "nota": "Series: datos simulados, 81 puntos de prueba; GRU consultado en su API real. NLP: 40 reportes NC simulados de prueba. ROI: estimación académica con supuestos explícitos."};
const REPORTES_NC = [["id_reporte", "fecha", "texto_reporte", "rol", "causa_real", "origen"], ["NC-006", "2026-11-07", "Linea L1, tapa de valvula: no conformidad detectada en la prueba de estanqueidad; hay puntos negros incrustados que no salen al limpiar.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-107", "2026-11-10", "Linea L2, tapa de valvula: no conformidad detectada en inspeccion final; medicion registrada en la unidad equivocada.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-063", "2026-11-08", "Linea L1, soporte: no conformidad detectada en el mecanizado; velocidad de llenado del molde excesiva.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-070", "2026-11-01", "Linea L3, soporte: no conformidad detectada en la prueba de estanqueidad; la broca se esta comiendo y el agujero sale ovalado. El operador de turno lo informo.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-026", "2026-11-13", "Linea L3, rodete: no conformidad detectada en inspeccion final; la misma marca aparece en la misma posicion pieza tras pieza.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-020", "2026-11-07", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; se apuro el desmoldeo y la pieza salio aun blanda. Se requiere revisar el procedimiento.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-071", "2026-11-02", "Linea L1, rodete: no conformidad detectada en control de recepcion del cliente; desgaste del noyo provoca diametro fuera de tolerancia.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-089", "2026-11-06", "Linea L3, rodete: no conformidad detectada en inspeccion final; la galga pasa no pasa estaba danada.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-025", "2026-11-12", "Linea L3, brida: no conformidad detectada en el mecanizado; herramienta de corte desgastada deja rebaba.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-103", "2026-11-06", "Linea L3, tapa de valvula: no conformidad detectada en inspeccion final; el turno de noche omitio la limpieza del area.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-037", "2026-11-10", "Linea L1, carcasa de bomba: no conformidad detectada durante la inspeccion visual; caida de la pieza desde el carro de transporte. Se detecto en el turno de tarde.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-001", "2026-11-02", "Linea L1, soporte: no conformidad detectada durante la inspeccion visual; se observa porosidad en la zona de la brida.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-031", "2026-11-04", "Linea L3, rodete: no conformidad detectada en el mecanizado; golpe durante la manipulacion en el traslado a bodega.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-093", "2026-11-10", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; poros abiertos tras el mecanizado del asiento.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-035", "2026-11-08", "Linea L3, rodete: no conformidad detectada durante la inspeccion visual; el operador no siguio el procedimiento de desbarbado.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-053", "2026-11-12", "Linea L1, rodete: no conformidad detectada en inspeccion final; impurezas visibles despues del granallado.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-039", "2026-11-12", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; caida de la pieza desde el carro de transporte.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-012", "2026-11-13", "Linea L2, carcasa de bomba: no conformidad detectada en control de recepcion del cliente; se apuro el desmoldeo y la pieza salio aun blanda. Se aparto el lote.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-013", "2026-11-14", "Linea L2, soporte: no conformidad detectada en la prueba de estanqueidad; presion de inyeccion inestable durante el ciclo.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-007", "2026-11-08", "Linea L1, carcasa de bomba: no conformidad detectada durante la inspeccion visual; la aleacion del lote de material no cumple la composicion especificada.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-018", "2026-11-05", "Linea L2, brida: no conformidad detectada en control de recepcion del cliente; se apuro el desmoldeo y la pieza salio aun blanda.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-050", "2026-11-09", "Linea L2, brida: no conformidad detectada en inspeccion final; el patron de referencia se cayo y nadie lo verifico despues.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-104", "2026-11-07", "Linea L1, tapa de valvula: no conformidad detectada en el mecanizado; alguien dejo la pieza en el piso junto al paso de la grua horquilla.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-009", "2026-11-10", "Linea L1, soporte: no conformidad detectada en inspeccion final; la aleacion del lote de material no cumple la composicion especificada.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-024", "2026-11-11", "Linea L1, soporte: no conformidad detectada en control de recepcion del cliente; el inserto ya cumplio su vida util y no fue reemplazado.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-027", "2026-11-14", "Linea L2, brida: no conformidad detectada en control de recepcion del cliente; el molde presenta desgaste en la linea de particion. Se aparto el lote.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-075", "2026-11-06", "Linea L1, brida: no conformidad detectada en el mecanizado; el turno de noche omitio la limpieza del area.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-091", "2026-11-08", "Linea L2, carcasa de bomba: no conformidad detectada en control de recepcion del cliente; poros abiertos tras el mecanizado del asiento.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-004", "2026-11-05", "Linea L3, soporte: no conformidad detectada en la prueba de estanqueidad; el certificado del proveedor no coincide con el analisis del laboratorio.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-067", "2026-11-12", "Linea L3, soporte: no conformidad detectada durante la inspeccion visual; cavidad danada genera marca repetitiva en todas las piezas.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-052", "2026-11-11", "Linea L2, carcasa de bomba: no conformidad detectada en control de recepcion del cliente; el espectrometro muestra cobre por sobre lo permitido en la carga.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-002", "2026-11-03", "Linea L1, tapa de valvula: no conformidad detectada en inspeccion final; el certificado del proveedor no coincide con el analisis del laboratorio.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-044", "2026-11-03", "Linea L1, soporte: no conformidad detectada en inspeccion final; el patron de referencia se cayo y nadie lo verifico despues.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-106", "2026-11-09", "Linea L2, brida: no conformidad detectada en control de recepcion del cliente; se salto el paso de revision porque faltaba gente. Se requiere revisar el procedimiento.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-069", "2026-11-14", "Linea L2, brida: no conformidad detectada durante la inspeccion visual; cavidad danada genera marca repetitiva en todas las piezas.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-048", "2026-11-07", "Linea L2, brida: no conformidad detectada en el mecanizado; al repetir el control en laboratorio la pieza si cumple. Se requiere revisar el procedimiento.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-066", "2026-11-11", "Linea L3, brida: no conformidad detectada en el mecanizado; el termopar marcaba bien pero el metal llego frio.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-084", "2026-11-01", "Linea L1, rodete: no conformidad detectada durante la inspeccion visual; el registro del equipo de control tiene la fecha vencida. El operador de turno lo informo.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-082", "2026-11-13", "Linea L2, soporte: no conformidad detectada en el mecanizado; se salto el paso de revision porque faltaba gente.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-017", "2026-11-04", "Linea L3, tapa de valvula: no conformidad detectada en control de recepcion del cliente; parametro de enfriamiento modificado sin autorizacion.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-028", "2026-11-01", "Linea L1, rodete: no conformidad detectada en la prueba de estanqueidad; el inserto ya cumplio su vida util y no fue reemplazado.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-096", "2026-11-13", "Linea L3, tapa de valvula: no conformidad detectada en inspeccion final; la camara de aire no se purgo y el llenado fue irregular. Se detecto en el turno de tarde.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-099", "2026-11-02", "Linea L2, tapa de valvula: no conformidad detectada en la prueba de estanqueidad; desgaste del noyo provoca diametro fuera de tolerancia. Se detecto en el turno de tarde.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-077", "2026-11-08", "Linea L3, tapa de valvula: no conformidad detectada durante la inspeccion visual; manipulacion sin proteccion dejo rayas en la cara sellante.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-105", "2026-11-08", "Linea L2, brida: no conformidad detectada durante la inspeccion visual; manipulacion sin proteccion dejo rayas en la cara sellante. El operador de turno lo informo.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-034", "2026-11-07", "Linea L2, carcasa de bomba: no conformidad detectada en inspeccion final; se uso la grua sin eslinga blanda y se marco el borde.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-095", "2026-11-12", "Linea L3, brida: no conformidad detectada durante la inspeccion visual; velocidad de llenado del molde excesiva. Se aparto el lote.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-010", "2026-11-11", "Linea L1, brida: no conformidad detectada durante la inspeccion visual; aparecen pequenas burbujas internas al cortar la pieza. Se detecto en el turno de tarde.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-072", "2026-11-03", "Linea L3, soporte: no conformidad detectada en la prueba de estanqueidad; el utillaje tiene un despostillado que se copia en la pieza. Se aparto el lote.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-060", "2026-11-05", "Linea L3, brida: no conformidad detectada durante la inspeccion visual; el termopar marcaba bien pero el metal llego frio.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-079", "2026-11-10", "Linea L2, rodete: no conformidad detectada en inspeccion final; manipulacion sin proteccion dejo rayas en la cara sellante.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-073", "2026-11-04", "Linea L1, soporte: no conformidad detectada durante la inspeccion visual; cavidad danada genera marca repetitiva en todas las piezas.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-008", "2026-11-09", "Linea L1, tapa de valvula: no conformidad detectada en la prueba de estanqueidad; hay puntos negros incrustados que no salen al limpiar.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-080", "2026-11-11", "Linea L1, brida: no conformidad detectada durante la inspeccion visual; el personal nuevo no recibio la instruccion de trabajo.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-085", "2026-11-02", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; la galga pasa no pasa estaba danada. Se requiere revisar el procedimiento.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-041", "2026-11-14", "Linea L2, soporte: no conformidad detectada en control de recepcion del cliente; error de medicion con el pie de metro en el diametro interior.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-087", "2026-11-04", "Linea L1, tapa de valvula: no conformidad detectada en inspeccion final; la galga pasa no pasa estaba danada. Se detecto en el turno de tarde.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-015", "2026-11-02", "Linea L3, carcasa de bomba: no conformidad detectada en la prueba de estanqueidad; presion de inyeccion inestable durante el ciclo.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-064", "2026-11-09", "Linea L3, tapa de valvula: no conformidad detectada en control de recepcion del cliente; la camara de aire no se purgo y el llenado fue irregular. Se aparto el lote.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-094", "2026-11-11", "Linea L1, soporte: no conformidad detectada en la prueba de estanqueidad; el espectrometro muestra cobre por sobre lo permitido en la carga. Se requiere revisar el procedimiento.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-032", "2026-11-05", "Linea L3, rodete: no conformidad detectada durante la inspeccion visual; se uso la grua sin eslinga blanda y se marco el borde.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-043", "2026-11-02", "Linea L3, soporte: no conformidad detectada en control de recepcion del cliente; el micrometro de la estacion dos no tiene calibracion vigente.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-023", "2026-11-10", "Linea L2, tapa de valvula: no conformidad detectada en inspeccion final; herramienta de corte desgastada deja rebaba. Se aparto el lote.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-040", "2026-11-13", "Linea L2, soporte: no conformidad detectada durante la inspeccion visual; quedaron mal apiladas y se rozaron entre ellas.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-049", "2026-11-08", "Linea L1, tapa de valvula: no conformidad detectada en la prueba de estanqueidad; el instrumento de control estaba fuera de calibracion. Se requiere revisar el procedimiento.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-055", "2026-11-14", "Linea L1, tapa de valvula: no conformidad detectada en el mecanizado; impurezas visibles despues del granallado. Se requiere revisar el procedimiento.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-092", "2026-11-09", "Linea L2, rodete: no conformidad detectada en el mecanizado; el metal recibido esta oxidado y contaminado.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-038", "2026-11-11", "Linea L2, brida: no conformidad detectada en el mecanizado; quedaron mal apiladas y se rozaron entre ellas.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-005", "2026-11-06", "Linea L1, carcasa de bomba: no conformidad detectada en la prueba de estanqueidad; presenta inclusiones no metalicas en la superficie mecanizada. Se aparto el lote.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-097", "2026-11-14", "Linea L3, soporte: no conformidad detectada en la prueba de estanqueidad; tiempo de ciclo reducido para recuperar produccion.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-045", "2026-11-04", "Linea L1, tapa de valvula: no conformidad detectada en inspeccion final; error de medicion con el pie de metro en el diametro interior.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-047", "2026-11-06", "Linea L2, rodete: no conformidad detectada en control de recepcion del cliente; el instrumento de control estaba fuera de calibracion.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-051", "2026-11-10", "Linea L2, brida: no conformidad detectada durante la inspeccion visual; colada con exceso de escoria atrapada en la pieza.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-030", "2026-11-03", "Linea L2, carcasa de bomba: no conformidad detectada en el mecanizado; la misma marca aparece en la misma posicion pieza tras pieza.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-033", "2026-11-06", "Linea L1, carcasa de bomba: no conformidad detectada en control de recepcion del cliente; golpe durante la manipulacion en el traslado a bodega.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-088", "2026-11-05", "Linea L2, rodete: no conformidad detectada en control de recepcion del cliente; el registro del equipo de control tiene la fecha vencida.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-086", "2026-11-03", "Linea L3, soporte: no conformidad detectada en el mecanizado; se rechazo la pieza pero la maquina tridimensional la acepta.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-016", "2026-11-03", "Linea L2, tapa de valvula: no conformidad detectada en inspeccion final; el horno no alcanzo el punto de trabajo antes de vaciar.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-068", "2026-11-13", "Linea L1, carcasa de bomba: no conformidad detectada en inspeccion final; la broca se esta comiendo y el agujero sale ovalado.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-042", "2026-11-01", "Linea L2, rodete: no conformidad detectada en control de recepcion del cliente; dos inspectores obtienen valores distintos en la misma cota.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-098", "2026-11-01", "Linea L2, rodete: no conformidad detectada en inspeccion final; se cambio la configuracion del equipo en el cambio de formato.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-021", "2026-11-08", "Linea L2, carcasa de bomba: no conformidad detectada durante la inspeccion visual; herramienta de corte desgastada deja rebaba.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-061", "2026-11-06", "Linea L3, carcasa de bomba: no conformidad detectada durante la inspeccion visual; tiempo de ciclo reducido para recuperar produccion.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-057", "2026-11-02", "Linea L1, brida: no conformidad detectada en inspeccion final; impurezas visibles despues del granallado.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-058", "2026-11-03", "Linea L2, rodete: no conformidad detectada en la prueba de estanqueidad; se ven huecos diminutos al pulir la cara del rodete. Se requiere revisar el procedimiento.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-108", "2026-11-11", "Linea L2, brida: no conformidad detectada en el mecanizado; el registro del equipo de control tiene la fecha vencida.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-029", "2026-11-02", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; matriz con fisura en la cavidad dos.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-101", "2026-11-04", "Linea L3, tapa de valvula: no conformidad detectada en inspeccion final; desgaste del noyo provoca diametro fuera de tolerancia. Se requiere revisar el procedimiento.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-083", "2026-11-14", "Linea L2, soporte: no conformidad detectada en inspeccion final; la galga pasa no pasa estaba danada. Se requiere revisar el procedimiento.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-065", "2026-11-10", "Linea L2, tapa de valvula: no conformidad detectada en la prueba de estanqueidad; tiempo de ciclo reducido para recuperar produccion. El operador de turno lo informo.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-003", "2026-11-04", "Linea L2, carcasa de bomba: no conformidad detectada en inspeccion final; se observa porosidad en la zona de la brida.", "referencia", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-011", "2026-11-12", "Linea L1, tapa de valvula: no conformidad detectada en el mecanizado; parametro de enfriamiento modificado sin autorizacion. Se requiere revisar el procedimiento.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-056", "2026-11-01", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; el espectrometro muestra cobre por sobre lo permitido en la carga.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-054", "2026-11-13", "Linea L3, tapa de valvula: no conformidad detectada en control de recepcion del cliente; se ven huecos diminutos al pulir la cara del rodete.", "prueba", "materia_prima", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-076", "2026-11-07", "Linea L2, carcasa de bomba: no conformidad detectada durante la inspeccion visual; se salto el paso de revision porque faltaba gente.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-100", "2026-11-03", "Linea L1, tapa de valvula: no conformidad detectada en el mecanizado; la broca se esta comiendo y el agujero sale ovalado. Se detecto en el turno de tarde.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-062", "2026-11-07", "Linea L3, brida: no conformidad detectada en la prueba de estanqueidad; se cambio la configuracion del equipo en el cambio de formato.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-022", "2026-11-09", "Linea L2, carcasa de bomba: no conformidad detectada en inspeccion final; el inserto ya cumplio su vida util y no fue reemplazado. Se aparto el lote.", "referencia", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-059", "2026-11-04", "Linea L3, brida: no conformidad detectada en control de recepcion del cliente; velocidad de llenado del molde excesiva.", "prueba", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-046", "2026-11-05", "Linea L1, brida: no conformidad detectada en inspeccion final; dos inspectores obtienen valores distintos en la misma cota.", "referencia", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-014", "2026-11-01", "Linea L1, brida: no conformidad detectada durante la inspeccion visual; se apuro el desmoldeo y la pieza salio aun blanda.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-036", "2026-11-09", "Linea L1, brida: no conformidad detectada en el mecanizado; quedaron mal apiladas y se rozaron entre ellas.", "referencia", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-074", "2026-11-05", "Linea L2, carcasa de bomba: no conformidad detectada en control de recepcion del cliente; el modelo de arena quedo con una esquina rota.", "prueba", "herramienta_molde", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-019", "2026-11-06", "Linea L2, soporte: no conformidad detectada en control de recepcion del cliente; presion de inyeccion inestable durante el ciclo.", "referencia", "ajuste_proceso", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-078", "2026-11-09", "Linea L1, brida: no conformidad detectada en la prueba de estanqueidad; alguien dejo la pieza en el piso junto al paso de la grua horquilla. Se requiere revisar el procedimiento.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-102", "2026-11-05", "Linea L3, carcasa de bomba: no conformidad detectada en el mecanizado; la broca se esta comiendo y el agujero sale ovalado.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-090", "2026-11-07", "Linea L2, brida: no conformidad detectada en control de recepcion del cliente; el registro del equipo de control tiene la fecha vencida. Se requiere revisar el procedimiento.", "prueba", "medicion_inspeccion", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-081", "2026-11-12", "Linea L3, carcasa de bomba: no conformidad detectada en la prueba de estanqueidad; manipulacion sin proteccion dejo rayas en la cara sellante.", "prueba", "operacion_manual", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-109", "2026-11-12", "Linea L3, rodete: no conformidad detectada en control de recepcion del cliente; medicion registrada en la unidad equivocada. Se detecto en el turno de tarde.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"], ["NC-110", "2026-11-13", "Linea L3, tapa de valvula: no conformidad detectada en el mecanizado; el registro del equipo de control tiene la fecha vencida.", "operacion", "", "SIMULADO_ACADEMICO_NO_REAL"]];

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
