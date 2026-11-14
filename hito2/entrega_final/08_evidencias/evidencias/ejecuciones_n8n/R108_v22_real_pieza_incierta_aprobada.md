# R108 · Ejecución REAL v2.2 · VG_TEST_022 (Defectuosa 56,34 %), LLM real, Gmail/Telegram reales, APROBAR humano

- Ejecución n8n: **108** · modo `manual` · estado **success**
- Inicio: 2026-11-14T21:40:18.497Z · fin: 2026-11-14T21:43:01.669Z
- Nodos con datos simulados (pin data, sin efectos externos): 0

| Orden | Nodo | Estado | Items | Simulado | Campos clave |
|---|---|---|---|---|---|
| 1 | Schedule Trigger | success | 1 | no | {} |
| 2 | Config | success | 1 | no | {} |
| 3 | HTTP Request1 | success | 1 | no | {} |
| 4 | If1 | success | 1 | no | {} |
| 5 | Search files and folders | success | 1 | no | {} |
| 6 | Search files and folders1 | success | 1 | no | {} |
| 7 | Hay_Imagenes_Pendientes | success | 1 | no | {} |
| 8 | Download file | success | 1 | no | {} |
| 9 | HTTP Request | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.5634, "archivo": "VG_TEST_022.jpeg"} |
| 10 | HTTP Request4 | success | 1 | no | {} |
| 11 | HTTP Request3 | success | 1 | no | {"tipo": "demostracion_simulada"} |
| 12 | Wait1 | success | 1 | no | {} |
| 13 | Split Out | success | 3 | no | {} |
| 14 | Append or update row in sheet | success | 3 | no | {"clave_unica": "2026-11-14/L1"} |
| 15 | Resumen_GRU | success | 1 | no | {"tipo": "RESUMEN_GRU"} |
| 16 | Lectura_NLP | success | 3 | no | {"estado": "PENDIENTE_VALIDACION"} |
| 17 | Leer_Reportes_NC | success | 3 | no | {} |
| 18 | Preparar_Textos_NLP | success | 1 | no | {} |
| 19 | Embeddings_Transformer_HF | success | 1 | no | {} |
| 20 | Unir_Textos_Embeddings | success | 1 | no | {} |
| 21 | Parsear_Embeddings | success | 1 | no | {"motivo_sin_transformer": "HTTP: 401 - {\"error\":\"Invalid username or password.\"}"} |
| 22 | Clasificar_NLP_Python | success | 1 | no | {"transformer_ejecutado": false, "motivo_sin_transformer": "HTTP: 401 - {\"error\":\"Invalid username or password.\"}", "metodo_usado_operacion": "Reglas", "causa_principal_operacion": "operacion_manual", "tipo": "NLP_TRANSFORMER", "mejor_metodo_en_prueba_f1": "No evaluable", "metricas_prueba": "{\"transformer\": null, \"reglas\": {\"n\": 40, \"accuracy\": 0.425, \"f1_macro\": 0.5154}}"} |
| 23 | Merge | success | 3 | no | {"tipo": "RESUMEN_GRU"} |
| 24 | Integracion_3_Modelos | success | 1 | no | {"estado": "PENDIENTE_VALIDACION_HUMANA", "alertas": "[{\"tipo\": \"PIEZA_DEFECTUOSA\", \"detalle\": \"VG_TEST_022.jpeg clasificada Defectuosa\"}, {\"tipo\": \"CONFIANZA_BAJA\", \"detalle", "tipo": "ANALISIS_INTEGRADO"} |
| 25 | LLM_Integrado | success | 1 | no | {} |
| 26 | Validacion_Seguridad_Final | success | 1 | no | {"fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "tipo": "ANALISIS_INTEGRADO_VALIDADO", "correcciones": [], "cifras_no_respaldadas": []} |
| 27 | Preparar_Registro_Integrado | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.5634, "archivo": "VG_TEST_022.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_022.jpeg clasificada Defectuosa  |
| 28 | Evitar_Notificaciones_Duplicadas | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.5634, "archivo": "VG_TEST_022.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_022.jpeg clasificada Defectuosa  |
| 29 | Guardar_Analisis_Integrado | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.5634, "archivo": "VG_TEST_022.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_022.jpeg clasificada Defectuosa  |
| 30 | Loop_Inspecciones | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.5634, "archivo": "VG_TEST_022.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_022.jpeg clasificada Defectuosa  |
| 31 | Notificacion_Analisis_Integrado | success | 1 | no | {} |
| 32 | Mover_A_Procesadas | success | 1 | no | {} |
| 33 | Notificacion_Telegram_Integrado | success | 1 | no | {} |
| 34 | Aprobacion_Humana_Integrada | success | 1 | no | {} |
| 35 | Validar_Respuesta_Humana | success | 1 | no | {} |
| 36 | Preparar_Aprobacion_Humana | success | 1 | no | {"archivo": "VG_TEST_022.jpeg", "estado": "ACCION_AUTORIZADA_POR_HUMANO", "decision_humana": "APROBAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14"} |
| 37 | Preparar_Registro_Final | success | 1 | no | {"archivo": "VG_TEST_022.jpeg", "estado": "ACCION_AUTORIZADA_POR_HUMANO", "decision_humana": "APROBAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14"} |
| 38 | Registrar_Decision_Humana | success | 1 | no | {"archivo": "VG_TEST_022.jpeg", "estado": "ACCION_AUTORIZADA_POR_HUMANO", "decision_humana": "APROBAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_022.jpeg/2026-11-14"} |
| 39 | Send a message2 | success | 1 | no | {} |
| 40 | Notificacion_Final_Telegram | success | 1 | no | {} |
| 41 | Loop_Inspecciones | success | 1 | no | {} |

## Lectura de la ejecución (todo real; ningún nodo simulado)
- ResNet18 clasificó `VG_TEST_022.jpeg` como **Defectuosa, 56,34 %**. Alertas: `PIEZA_DEFECTUOSA`, `CONFIANZA_BAJA` (56,34 % < 90 %) y las alertas del GRU simulado.
- GPT-4o mini real: `LLM_VALIDADO`, prioridad alta, 0 correcciones, 0 cifras no respaldadas. Recomendación: *"Apartar la pieza para inspección humana y no aprobar automáticamente…"*.
- Se enviaron el informe Gmail (con enlace al panel), el Telegram y el correo de aprobación.
- Decisión humana real **APROBAR**: queda `ACCION_AUTORIZADA_POR_HUMANO` (2026-11-14 18:42:57, hora de Chile), registrada en Sheets. Se enviaron el Gmail y el Telegram finales y la imagen se movió a Procesadas.
- APROBAR autoriza la acción propuesta (apartar e inspeccionar manualmente). **No** libera la pieza.
- Estado: `success` (21:40:18Z → 21:43:01Z).
