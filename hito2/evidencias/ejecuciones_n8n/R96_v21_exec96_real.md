# Ejecución REAL v2.1 (ejecución 96, workflow v2.1 INTEGRADO, 13-nov-2026): imagen real, LLM real, Gmail/Telegram reales, decisión humana real

- Ejecución n8n: **96** · modo `manual` · estado **success**
- Inicio: 2026-11-13T21:36:31.697Z · fin: 2026-11-13T21:40:50.665Z
- Nodos con datos simulados (pin data, sin efectos externos): 0

| Orden | Nodo | Estado | Items | Simulado | Campos clave |
|---|---|---|---|---|---|
| 1 | Schedule Trigger | success | 1 | no | {} |
| 2 | HTTP Request1 | success | 1 | no | {} |
| 3 | If1 | success | 1 | no | {} |
| 4 | Wait | success | 1 | no | {} |
| 5 | HTTP Request2 | success | 1 | no | {} |
| 6 | If2 | success | 1 | no | {} |
| 7 | Search files and folders | success | 1 | no | {} |
| 8 | Search files and folders1 | success | 1 | no | {} |
| 9 | Download file | success | 1 | no | {} |
| 10 | HTTP Request | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9949, "archivo": "VG_TEST_015.jpeg"} |
| 11 | Message a model | success | 1 | no | {} |
| 12 | Code in JavaScript | success | 1 | no | {} |
| 13 | Append row in sheet | success | 1 | no | {} |
| 14 | If | success | 1 | no | {} |
| 15 | Move file1 | success | 1 | no | {} |
| 16 | Send a text message | success | 1 | no | {} |
| 17 | HTTP Request4 | success | 1 | no | {} |
| 18 | Wait1 | success | 1 | no | {} |
| 19 | HTTP Request3 | success | 1 | no | {"tipo": "demostracion_simulada"} |
| 20 | Split Out | success | 2 | no | {} |
| 21 | Append or update row in sheet | success | 2 | no | {} |
| 22 | Resumen_GRU | success | 1 | no | {"tipo": "RESUMEN_GRU"} |
| 23 | Lectura_NLP | success | 2 | no | {"estado": "PENDIENTE_VALIDACION"} |
| 24 | Merge | success | 2 | no | {"tipo": "RESUMEN_GRU"} |
| 25 | Integracion_3_Modelos | success | 1 | no | {"estado": "PENDIENTE_VALIDACION_HUMANA", "tipo": "ANALISIS_INTEGRADO"} |
| 26 | LLM_Integrado | success | 1 | no | {} |
| 27 | Validacion_Seguridad_Final | success | 1 | no | {"prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "tipo": "ANALISIS_INTEGRADO_VALIDADO", "correcciones": null, "cifras_no_respaldadas": null} |
| 28 | Preparar_Registro_Integrado | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9949, "archivo": "VG_TEST_015.jpeg", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_015.jpeg/2026-10-28"} |
| 29 | Guardar_Analisis_Integrado | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9949, "archivo": "VG_TEST_015.jpeg", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_015.jpeg/2026-10-28"} |
| 30 | Evitar_Notificaciones_Duplicadas | success | 1 | no | {"clasificacion": "Defectuosa", "confianza": 0.9949, "archivo": "VG_TEST_015.jpeg", "prioridad": "alta", "estado": "PENDIENTE_VALIDACION_HUMANA", "validacion_humana_realizada": false, "clave_unica": "INTEGRADO/VG_TEST_015.jpeg/2026-10-28"} |
| 31 | Notificacion_Analisis_Integrado | success | 1 | no | {} |
| 32 | Notificacion_Telegram_Integrado | success | 1 | no | {} |
| 33 | Aprobacion_Humana_Integrada | success | 1 | no | {} |
| 34 | Validar_Respuesta_Humana | success | 1 | no | {} |
| 35 | Preparar_Rechazo_Humano | success | 1 | no | {"estado": "ACCION_RECHAZADA_POR_HUMANO", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_015.jpeg/2026-10-28"} |
| 36 | Registrar_Decision_Humana | success | 1 | no | {"estado": "ACCION_RECHAZADA_POR_HUMANO", "validacion_humana_realizada": true, "clave_unica": "INTEGRADO/VG_TEST_015.jpeg/2026-10-28"} |
