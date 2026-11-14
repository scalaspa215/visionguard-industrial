# Plan de pruebas y evidencias — VisionGuard v2.2

Estado: **V** = verificado en este paquete (reproducible) · **P** = pendiente de ejecutar en n8n por el equipo, con capturas.

## A. Pruebas automáticas (ya ejecutadas)

| # | Prueba | Comando | Resultado |
|---|---|---|---|
| A1 | 15 casos de los nodos Code (seguridad, JSON, alucinación, errores) | `node pruebas/harness_nodos.js` | **V** 15/15 OK (`resultados_pruebas_nodos.json`) |
| A2 | Nodo Python = gemelo JS | `python pruebas/probar_nodo_python.py` | **V** idénticos |
| A3 | Integridad del workflow y export sin secretos | `node pruebas/verificar_workflow.js` | **V** 17/17 OK (`resultado_verificacion_workflow.txt`) |
| A4 | Series: 7 modelos, GRU por API real | `python python/series/comparar_series.py` | **V** `resultados_series.json` |
| A5 | NLP reglas en 40 reportes de prueba | `python python/nlp/evaluar_nlp.py` | **V** reglas 0,425 / 0,515; Transformer MiniLM 0,375 / 0,347 (CPU local) |
| A6 | ROI y sensibilidad | `python python/negocio/roi_visionguard.py` | **V** `roi_resultados.json`, `roi_escenarios.png` |
| A7 | Tablero Apps Script compila | `node -e "new Function(...)"` | **V** |

## B. Pruebas de extremo a extremo en n8n (capturar cada una)

Captura obligatoria por caso: la ejecución en n8n (todos los nodos en verde) + el correo Gmail + el mensaje Telegram + la fila en Sheets.

| # | Caso | Preparación | Resultado esperado | Estado |
|---|---|---|---|---|
| B1 | Pieza defectuosa | `VG_H2_DEF_01.jpeg` (de `def_front`) en Pendientes | Prioridad ALTA, alerta 🚨, correo de aprobación; al **Rechazar**: `ACCION_RECHAZADA_POR_HUMANO` + Gmail/Telegram final | P |
| B2 | Pieza correcta | `VG_H2_OK_01.jpeg` (de `ok_front`) | Prioridad baja/media, igual pide validación; al **Aprobar**: `ACCION_AUTORIZADA_POR_HUMANO` | P |
| B3 | Pieza con confianza baja | Imagen borrosa o recortada | Alerta `CONFIANZA_BAJA`, prioridad alta | P |
| B4 | Carpeta vacía | Pendientes sin imágenes | Gmail + Telegram "sin inspecciones pendientes" | P |
| B5 | Archivo no imagen | Un `.jpeg` renombrado desde un `.txt` | La API responde 400 → alerta `ERROR_INFERENCIA_IMAGEN`; el resto sigue | P |
| B6 | Sin token Hugging Face | Quitar la credencial del nodo HF | `nlp_transformer_ejecutado = false`; el aviso dice "solo reglas" | P |
| B7 | Duplicado | Volver a poner la misma imagen el mismo día | No se crea una 2.ª fila ni una 2.ª notificación | P |
| B8 | Sin respuesta humana | No responder (o fijar el límite en 5 min para la prueba) | `SIN_RESPUESTA_HUMANA_ESCALAR` + aviso | P |
| B9 | Error de un nodo | Cambiar temporalmente la URL de `/pronosticos-demo` | El Error Handler envía Gmail y Telegram | P |

**Rúbrica:** basta con 3 ejecuciones exitosas con datos distintos (B1, B2, B3). B4–B9 son evidencia de robustez.

## C. Seguridad (no negociable)
- Ninguna prueba debe responder "Aprobar" sobre una pieza Defectuosa como si quedara liberada. Aprobar autoriza la **acción de inspección**, no la pieza.
- No activar el workflow en producción hasta desactivar la v2.1.
- No enviar a destinatarios distintos del responsable de prueba.
