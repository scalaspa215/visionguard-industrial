# Plan de pruebas y evidencias — VisionGuard v2.2 (estado al 14-nov-2026)

**Tipos de evidencia**
- **U** · prueba unitaria local: el código de los nodos corre fuera de n8n.
- **I** · prueba de integración **en n8n Cloud** con `test_workflow`. El motor real de n8n ejecuta todos los nodos Code (JS y Python), If, Merge, Loop, Wait y Dedupe. Los nodos con efectos externos (Gmail, Telegram, Sheets, Drive, HTTP, LLM) reciben **datos simulados (pin data)**, así que no se envía nada real.
- **R** · ejecución real con imagen real, LLM real, Gmail y Telegram reales y decisión humana real.

## A. Pruebas automáticas locales

| # | Prueba | Comando | Resultado |
|---|---|---|---|
| A1 | 15 casos de los nodos Code | `node pruebas/harness_nodos.js` | 15/15 OK |
| A2 | Nodo Python = gemelo JS | `python pruebas/probar_nodo_python.py` | idénticos |
| A3 | Integridad del workflow y export sin secretos | `node pruebas/verificar_workflow.js` | 17/17 OK |
| A4 | Series: 7 modelos, GRU por la API real | `python python/series/comparar_series.py` | `resultados_series.json` |
| A5 | NLP: Transformer MiniLM vs reglas | `python python/nlp/evaluar_nlp.py` | reglas 0,425 / 0,515 · MiniLM 0,375 / 0,347 |
| A6 | ROI y sensibilidad | `python python/negocio/roi_visionguard.py` | `roi_resultados.json` |

## B. Pruebas de integración en n8n (workflow `VisionGuard v2.2 - Hito 2 FINAL`)

| Caso | Ejec. | Tipo | Entrada | Esperado | Observado | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| — | 100 | I | Defectuosa + fallo de HF | El flujo completo | **Falla** en `Clasificar_NLP_Python`: `name 'hasattr' is not defined` | `T0_exec100_*.md` | Bug detectado → corregido |
| B1 + B6 | 101 | I | Defectuosa 99,63 %, sin pedido de revisión de la API, HF caído (401), LLM válido, humano **rechaza** | Prioridad alta; revisión forzada; NLP solo con reglas; registro `ACCION_RECHAZADA_POR_HUMANO` | Coincide (5 alertas, `LLM_VALIDADO`, `RECHAZAR` con fecha) | `T1_exec101_*.md` | Verificado (I) |
| B3 + B8 | 102 | I | Correcta 72,76 % (confianza baja), JSON del LLM truncado, ruta Transformer (embeddings sintéticos), **sin respuesta** humana | Alerta `CONFIANZA_BAJA`; respaldo determinista; `SIN_RESPUESTA_HUMANA_ESCALAR` | Coincide | `T2_exec102_*.md` | Verificado (I) |
| B4 | 103 | I | Carpeta vacía | Gmail + Telegram "sin pendientes"; sin LLM ni registros | Coincide; Integración devuelve 0 ítems sin error | `T3_exec103_*.md` | Verificado (I) |
| B9 (parcial) | 104 | I | `/health` 503 dos veces | Espera de 60 s, luego Gmail + Telegram "API no disponible" | Coincide | `T4_exec104_*.md` | Verificado (I). El disparo real del Error Handler requiere una ejecución de producción |
| B5 + B7 | 105 | I | 1 archivo corrupto (400) + la misma imagen de T1 el mismo día | Alerta `ERROR_INFERENCIA_IMAGEN`; la deduplicación descarta la repetida, sin 2.º registro ni aviso | Coincide: el archivo corrupto se aísla; el duplicado se descarta antes de Sheets | `T5_exec105_*.md` | Verificado (I) |
| R-1 | 96 (v2.1) | R | `VG_TEST_015.jpeg` real | Flujo integrado completo con decisión humana real | Defectuosa 99,49 %, LLM real, Gmail + Telegram enviados, rechazo humano real a las 21:40:49Z | `R96_v21_exec96_real.md` | Verificado (R, versión v2.1) |
| B1–B3 reales v2.2 | — | R | 3 imágenes reales nuevas | Correo, Telegram y aprobación reales | — | — | **Pendiente: requiere autorización de envío y subir 3 imágenes** |

## C. Seguridad (no negociable)
- Ninguna prueba aprueba como liberada una pieza Defectuosa. Aprobar solo autoriza la **acción de inspección**.
- No activar la v2.2 en producción sin antes **desactivar** el workflow del Hito 1 (`VisionGuard - Industrial Quality Control`). Sigue activo y procesa la misma carpeta de Drive todos los días a las 11:00 UTC.
- Las pruebas de integración no envían correos ni mensajes reales: todos los nodos con efectos externos están simulados con pin data.
