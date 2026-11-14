# T1 · Ejecución 101 · Pieza defectuosa + fallo de Hugging Face + rechazo humano (pin data)

- Ejecución n8n: **101** · modo `manual` · estado **success**
- Inicio: 2026-11-14T21:19:47.682Z · fin: 2026-11-14T21:21:21.669Z
- Nodos con datos simulados (pin data, sin efectos externos): 26

| Orden | Nodo | Estado | Items | Simulado | Campos clave |
|---|---|---|---|---|---|
| 1 | Schedule Trigger | success | 1 | sí | {} |
| 2 | Config | success | 1 | no | {} |
| 3 | HTTP Request1 | success | 1 | sí | {} |
| 4 | If1 | success | 1 | no | {} |
| 5 | Search files and folders | success | 1 | sí | {} |
| 6 | Hay_Imagenes_Pendientes | success | 1 | no | {} |
| 7 | Search files and folders1 | success | 1 | sí | {} |
| 8 | Download file | success | 1 | sí | {} |
| 9 | HTTP Request | success | 1 | sí | {"clasificacion": "Defectuosa", "confianza": 0.9963, "archivo": "VG_PIN_T1_DEF.jpeg"} |
| 10 | HTTP Request4 | success | 1 | sí | {} |
| 11 | Wait1 | success | 1 | no | {} |
| 12 | HTTP Request3 | success | 1 | sí | {"tipo": "demostracion_simulada"} |
| 13 | Split Out | success | 2 | no | {} |
| 14 | Append or update row in sheet | success | 1 | sí | {"clave_unica": "2026-11-14/L1"} |
| 15 | Resumen_GRU | success | 1 | no | {"tipo": "RESUMEN_GRU"} |
| 16 | Lectura_NLP | success | 1 | sí | {"estado": "PENDIENTE_VALIDACION"} |
| 17 | Leer_Reportes_NC | success | 2 | sí | {} |
| 18 | Preparar_Textos_NLP | success | 1 | no | {} |
| 19 | Embeddings_Transformer_HF | success | 1 | sí | {} |
| 20 | Unir_Textos_Embeddings | success | 1 | no | {} |
| 21 | Parsear_Embeddings | success | 1 | no | {"motivo_sin_transformer": "HTTP: PRUEBA_PIN: 401 Unauthorized (fallo simulado de Hugging Face)"} |
| 22 | Clasificar_NLP_Python | success | 1 | no | {"transformer_ejecutado": false, "motivo_sin_transformer": "HTTP: PRUEBA_PIN: 401 Unauthorized (fallo simulado de Hugging Face)", "metodo_usado_operacion": "Reglas", "causa_principal_operacion": "medicion_inspeccion", "tipo": "NLP_TRANSFORMER", "mejor_metodo_en_prueba_f1": "No evaluable", "metricas_prueba": "{\"transformer\": null, \"reglas\": {\"n\": 5, \"accuracy\": 0.8, \"f1_macro\": 0.7333}}"} |
| 23 | Merge | success | 2 | no | {"tipo": "RESUMEN_GRU"} |
| 24 | Integracion_3_Modelos | success | 1 | no | {"estado": "PENDIENTE_VALIDACION_HUMANA", "alertas": "[{\"tipo\": \"PIEZA_DEFECTUOSA\", \"detalle\": \"VG_PIN_T1_DEF.jpeg clasificada Defectuosa\"}, {\"tipo\": \"INCONSISTENCIA_API\", \"d", "tipo": "ANALISIS_INTEGRADO"} |
| 25 | LLM_Integrado | success | 1 | sí | {} |
| 26 | Validacion_Seguridad_Final | success | 1 | no | {"fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "tipo": "ANALISIS_INTEGRADO_VALIDADO", "correcciones": [], "cifras_no_respaldadas": []} |
| 27 | Preparar_Registro_Integrado | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9963, "archivo": "VG_PIN_T1_DEF.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_PIN_T1_DEF.jpeg clasificada Defec |
| 28 | Evitar_Notificaciones_Duplicadas | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9963, "archivo": "VG_PIN_T1_DEF.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_PIN_T1_DEF.jpeg clasificada Defec |
| 29 | Guardar_Analisis_Integrado | success | 1 | sí | {"clasificacion": "Defectuosa", "confianza": 0.9963, "archivo": "VG_PIN_T1_DEF.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA"} |
| 30 | Loop_Inspecciones | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9963, "archivo": "VG_PIN_T1_DEF.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA"} |
| 31 | Notificacion_Analisis_Integrado | success | 1 | sí | {} |
| 32 | Aprobacion_Humana_Integrada | success | 1 | sí | {} |
| 33 | Mover_A_Procesadas | success | 1 | sí | {} |
| 34 | Notificacion_Telegram_Integrado | success | 1 | sí | {} |
| 35 | Validar_Respuesta_Humana | success | 1 | no | {} |
| 36 | Preparar_Rechazo_Humano | success | 1 | no | {"archivo": "VG_PIN_T1_DEF.jpeg", "estado": "ACCION_RECHAZADA_POR_HUMANO", "decision_humana": "RECHAZAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14"} |
| 37 | Preparar_Registro_Final | success | 1 | no | {"archivo": "VG_PIN_T1_DEF.jpeg", "estado": "ACCION_RECHAZADA_POR_HUMANO", "decision_humana": "RECHAZAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14"} |
| 38 | Notificacion_Final_Telegram | success | 1 | sí | {} |
| 39 | Registrar_Decision_Humana | success | 1 | sí | {"estado": "ACCION_RECHAZADA_POR_HUMANO", "clave_unica": "INTEGRADO/VG_PIN_T1_DEF.jpeg/2026-11-14"} |
| 40 | Send a message2 | success | 1 | sí | {} |
| 41 | Loop_Inspecciones | success | 1 | no | {} |
