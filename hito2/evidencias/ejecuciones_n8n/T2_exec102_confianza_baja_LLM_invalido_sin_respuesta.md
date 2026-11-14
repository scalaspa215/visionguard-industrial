# T2 · Ejecución 102 · Confianza baja + JSON inválido del LLM + ruta Transformer + sin respuesta humana (pin data)

- Ejecución n8n: **102** · modo `manual` (`test_workflow` con pin data) · estado **success**
- Inicio 2026-11-14T21:22:24Z · fin 21:23:57Z (incluye la espera de 90 s de `Wait1`)
- Datos simulados: imagen `VG_PIN_T2_BAJA.jpeg` (Correcta, 72,76 %, la API exige revisión); 13 reportes NC reales del CSV simulado; **embeddings sintéticos de 4 dimensiones** (solo para probar la ruta de cálculo, no el modelo); LLM con respuesta JSON truncada; aprobación sin respuesta (`data: {}`).
- Gmail, Telegram, Sheets y Drive están simulados (pin data): **no se envió nada real**.

| Nodo (código real ejecutado en n8n) | Resultado observado |
|---|---|
| `Hay_Imagenes_Pendientes` | rama verdadera → `Download file` |
| `Clasificar_NLP_Python` (Python nativo) | `transformer_ejecutado: true`; métricas en 5 reportes de prueba: Transformer acc 1,0 / F1 1,0 (embeddings sintéticos), reglas acc 0,8 / F1 0,733; `metodo_usado_operacion: Transformer`; causa principal `medicion_inspeccion` |
| `Integracion_3_Modelos` | 3 alertas: `CONFIANZA_BAJA` (72,76 % < 90 %), `DISCREPANCIA_MODELOS_SERIE` (L2 6,48 vs 8,05), `PRONOSTICO_SOBRE_UMBRAL` (L3 7,89 ≥ 7,5) |
| `Validacion_Seguridad_Final` | `json_valido: false`, falla "JSON invalido del LLM." → `fuente_analisis: RESPALDO_DETERMINISTA`, prioridad **alta**, `aprobacion_automatica: false` |
| `Preparar_Registro_Integrado` | clave `INTEGRADO\|VG_PIN_T2_BAJA.jpeg\|2026-11-14`, `nlp_f1_transformer 1`, `nlp_f1_reglas 0.7333`, `decision_humana PENDIENTE` |
| `Evitar_Notificaciones_Duplicadas` | 1 item pasa (clave nueva) |
| `Loop_Inspecciones` → Gmail, Telegram, Mover, Aprobación | ejecutados (simulados) |
| `Validar_Respuesta_Humana` | rama falsa (sin `approved`) |
| `Preparar_Rechazo_Humano` | `estado: SIN_RESPUESTA_HUMANA_ESCALAR`, `decision_humana: SIN_RESPUESTA`, `validacion_humana_realizada: false`, fecha registrada |
| `Registrar_Decision_Humana` → `Send a message2` → `Notificacion_Final_Telegram` → `Loop_Inspecciones` (done) | ejecutados; el bucle termina |

**Conclusión:** el respaldo determinista evita que un JSON roto detenga el flujo, la pieza queda con prioridad alta y nunca aprobada, y la falta de respuesta humana queda trazada para escalar. La ruta Transformer del nodo Python calcula los centroides y las métricas dentro de n8n. Las cifras 1,0 provienen de vectores sintéticos y **no** miden el modelo real (ver `resultados_nlp.json`: F1 0,347).
