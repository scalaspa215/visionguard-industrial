# R107 · Ejecución REAL v2.2 · 2 piezas reales (VG_TEST_021, VG_TEST_020), LLM real, Gmail/Telegram reales, decisiones humanas reales

- Ejecución n8n: **107** · modo `manual` · estado **success**
- Inicio: 2026-11-14T21:35:05.033Z · fin: 2026-11-14T21:40:04.494Z
- Nodos con datos simulados (pin data, sin efectos externos): 0

| Orden | Nodo | Estado | Items | Simulado | Campos clave |
|---|---|---|---|---|---|
| 1 | Schedule Trigger | success | 1 | no | {} |
| 2 | Config | success | 1 | no | {} |
| 3 | HTTP Request1 | success | 1 | no | {} |
| 4 | If1 | success | 1 | no | {} |
| 5 | Search files and folders | success | 1 | no | {} |
| 6 | Search files and folders1 | success | 2 | no | {} |
| 7 | Hay_Imagenes_Pendientes | success | 2 | no | {} |
| 8 | Download file | success | 2 | no | {} |
| 9 | HTTP Request | success | 2 | no | {"clasificacion": "Defectuosa", "confianza": 0.9178, "archivo": "VG_TEST_021.jpeg"} |
| 10 | HTTP Request4 | success | 1 | no | {} |
| 11 | Wait1 | success | 1 | no | {} |
| 12 | HTTP Request3 | success | 1 | no | {"tipo": "demostracion_simulada"} |
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
| 24 | Integracion_3_Modelos | success | 1 | no | {"estado": "PENDIENTE_VALIDACION_HUMANA", "alertas": "[{\"tipo\": \"PIEZA_DEFECTUOSA\", \"detalle\": \"VG_TEST_021.jpeg clasificada Defectuosa\"}, {\"tipo\": \"INCONSISTENCIA_API\", \"det", "tipo": "ANALISIS_INTEGRADO"} |
| 25 | LLM_Integrado | success | 1 | no | {} |
| 26 | Validacion_Seguridad_Final | success | 1 | no | {"fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "tipo": "ANALISIS_INTEGRADO_VALIDADO", "correcciones": [], "cifras_no_respaldadas": []} |
| 27 | Preparar_Registro_Integrado | success | 2 | no | {"clasificacion": "Defectuosa", "confianza": 0.9178, "archivo": "VG_TEST_021.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_021.jpeg clasificada Defectuosa  |
| 28 | Evitar_Notificaciones_Duplicadas | success | 2 | no | {"clasificacion": "Defectuosa", "confianza": 0.9178, "archivo": "VG_TEST_021.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_021.jpeg clasificada Defectuosa  |
| 29 | Guardar_Analisis_Integrado | success | 2 | no | {"clasificacion": "Defectuosa", "confianza": 0.9178, "archivo": "VG_TEST_021.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_021.jpeg clasificada Defectuosa  |
| 30 | Loop_Inspecciones | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9178, "archivo": "VG_TEST_021.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_021.jpeg clasificada Defectuosa  |
| 31 | Notificacion_Analisis_Integrado | success | 1 | no | {} |
| 32 | Mover_A_Procesadas | success | 1 | no | {} |
| 33 | Notificacion_Telegram_Integrado | success | 1 | no | {} |
| 34 | Aprobacion_Humana_Integrada | success | 1 | no | {} |
| 35 | Validar_Respuesta_Humana | success | 1 | no | {} |
| 36 | Preparar_Rechazo_Humano | success | 1 | no | {"archivo": "VG_TEST_021.jpeg", "estado": "ACCION_RECHAZADA_POR_HUMANO", "decision_humana": "RECHAZAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14"} |
| 37 | Preparar_Registro_Final | success | 1 | no | {"archivo": "VG_TEST_021.jpeg", "estado": "ACCION_RECHAZADA_POR_HUMANO", "decision_humana": "RECHAZAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14"} |
| 38 | Registrar_Decision_Humana | success | 1 | no | {"archivo": "VG_TEST_021.jpeg", "estado": "ACCION_RECHAZADA_POR_HUMANO", "decision_humana": "RECHAZAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_021.jpeg/2026-11-14"} |
| 39 | Send a message2 | success | 1 | no | {} |
| 40 | Notificacion_Final_Telegram | success | 1 | no | {} |
| 41 | Loop_Inspecciones | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.7408, "archivo": "VG_TEST_020.jpeg", "fuente_analisis": "LLM_VALIDADO", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "decision_humana": "PENDIENTE", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_020.jpeg/2026-11-14", "tiene_alertas": true, "alertas": "PIEZA_DEFECTUOSA: VG_TEST_020.jpeg clasificada Defectuosa  |
| 42 | Notificacion_Analisis_Integrado | success | 1 | no | {} |
| 43 | Mover_A_Procesadas | success | 1 | no | {} |
| 44 | Notificacion_Telegram_Integrado | success | 1 | no | {} |
| 45 | Aprobacion_Humana_Integrada | success | 1 | no | {} |
| 46 | Validar_Respuesta_Humana | success | 1 | no | {} |
| 47 | Preparar_Aprobacion_Humana | success | 1 | no | {"archivo": "VG_TEST_020.jpeg", "estado": "ACCION_AUTORIZADA_POR_HUMANO", "decision_humana": "APROBAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_020.jpeg/2026-11-14"} |
| 48 | Preparar_Registro_Final | success | 1 | no | {"archivo": "VG_TEST_020.jpeg", "estado": "ACCION_AUTORIZADA_POR_HUMANO", "decision_humana": "APROBAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_020.jpeg/2026-11-14"} |
| 49 | Registrar_Decision_Humana | success | 1 | no | {"archivo": "VG_TEST_020.jpeg", "estado": "ACCION_AUTORIZADA_POR_HUMANO", "decision_humana": "APROBAR", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_020.jpeg/2026-11-14"} |
| 50 | Send a message2 | success | 1 | no | {} |
| 51 | Notificacion_Final_Telegram | success | 1 | no | {} |
| 52 | Loop_Inspecciones | success | 2 | no | {} |

## Lectura de la ejecución (todo real; ningún nodo simulado)
- **Datos reales:** ResNet18 en Render clasificó `VG_TEST_021.jpeg` como Defectuosa (91,78 %) y `VG_TEST_020.jpeg` como Defectuosa (74,08 %; la API exigió revisión).
- **Alertas:** `PIEZA_DEFECTUOSA` en ambas. `INCONSISTENCIA_API` en VG_TEST_021, donde la API no exigió revisión y se forzó. `CONFIANZA_BAJA` en VG_TEST_020 (74,08 % < 90 %). Además, `DISCREPANCIA_MODELOS_SERIE` y `PRONOSTICO_SOBRE_UMBRAL` del GRU simulado.
- **GPT-4o mini real:** `fuente_analisis = LLM_VALIDADO`, prioridad alta, 0 correcciones, 0 cifras no respaldadas y 0 frases de aprobación sospechosas.
  - Recomendación: *"Aislar las piezas clasificadas como defectuosas, solicitando inspección humana para cada una…"*.
  - El LLM declaró que el NLP usó reglas porque el Transformer no se ejecutó (Hugging Face 401). No inventó esa ejecución.
- **Notificaciones:** se enviaron 2 informes Gmail con el botón al panel, 2 Telegram y 2 correos de aprobación.
- **Decisiones humanas reales:**
  - `VG_TEST_021.jpeg` → **RECHAZAR** → `ACCION_RECHAZADA_POR_HUMANO` (2026-11-14 18:39:15, hora de Chile).
  - `VG_TEST_020.jpeg` → **APROBAR** → `ACCION_AUTORIZADA_POR_HUMANO` (2026-11-14 18:40:00). Aprobar autoriza la acción de apartar e inspeccionar; no libera la pieza.
- **Registro y avisos finales:** ambas decisiones se escribieron en `Analisis_Integrado`. Se enviaron 2 Gmail y 2 Telegram de decisión final. Las 2 imágenes se movieron a `Inspecciones_Procesadas`.
- **Resultado:** estado `success` (21:35:05Z → 21:40:04Z).
