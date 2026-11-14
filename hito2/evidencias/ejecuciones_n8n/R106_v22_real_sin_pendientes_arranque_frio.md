# R106 · Ejecución REAL v2.2 · Carpeta vacía (B4 real) + arranque en frío de Render con reintento

- Ejecución n8n: **106** · modo `manual` · estado **success**
- Inicio: 2026-11-14T21:30:37.657Z · fin: 2026-11-14T21:34:00.524Z
- Nodos con datos simulados (pin data, sin efectos externos): 1

| Orden | Nodo | Estado | Items | Simulado | Campos clave |
|---|---|---|---|---|---|
| 1 | Schedule Trigger | success | 1 | sí | {} |
| 2 | Config | success | 1 | no | {} |
| 3 | HTTP Request1 | success | 1 | no | {} |
| 4 | If1 | success | 1 | no | {} |
| 5 | Wait | success | 1 | no | {} |
| 6 | HTTP Request2 | success | 1 | no | {} |
| 7 | If2 | success | 1 | no | {} |
| 8 | Search files and folders | success | 1 | no | {} |
| 9 | Search files and folders1 | success | 1 | no | {} |
| 10 | Hay_Imagenes_Pendientes | success | 1 | no | {} |
| 11 | Aviso_Sin_Pendientes_Gmail | success | 1 | no | {} |
| 12 | Aviso_Sin_Pendientes_Telegram | success | 1 | no | {} |
| 13 | HTTP Request4 | success | 1 | no | {} |
| 14 | HTTP Request3 | success | 1 | no | {"tipo": "demostracion_simulada"} |
| 15 | Wait1 | success | 1 | no | {} |
| 16 | Split Out | success | 2 | no | {} |
| 17 | Append or update row in sheet | success | 2 | no | {"clave_unica": "2026-11-14/L1"} |
| 18 | Resumen_GRU | success | 1 | no | {"tipo": "RESUMEN_GRU"} |
| 19 | Lectura_NLP | success | 2 | no | {"estado": "PENDIENTE_VALIDACION"} |
| 20 | Leer_Reportes_NC | success | 2 | no | {} |
| 21 | Preparar_Textos_NLP | success | 1 | no | {} |
| 22 | Embeddings_Transformer_HF | success | 1 | no | {} |
| 23 | Unir_Textos_Embeddings | success | 1 | no | {} |
| 24 | Parsear_Embeddings | success | 1 | no | {"motivo_sin_transformer": "HTTP: 401 - {\"error\":\"Invalid username or password.\"}"} |
| 25 | Clasificar_NLP_Python | success | 1 | no | {"transformer_ejecutado": false, "motivo_sin_transformer": "HTTP: 401 - {\"error\":\"Invalid username or password.\"}", "metodo_usado_operacion": "Reglas", "causa_principal_operacion": "operacion_manual", "tipo": "NLP_TRANSFORMER", "mejor_metodo_en_prueba_f1": "No evaluable", "metricas_prueba": "{\"transformer\": null, \"reglas\": {\"n\": 40, \"accuracy\": 0.425, \"f1_macro\": 0.5154}}"} |
| 26 | Merge | success | 2 | no | {"tipo": "RESUMEN_GRU"} |
| 27 | Integracion_3_Modelos | success | 0 | no | {} |

## Lectura de la ejecución (servicios reales; ningún nodo simulado)
- `HTTP Request1` (`/health` ResNet18) recibió **503** por el arranque en frío de Render. `If1` tomó la rama falsa, `Wait` esperó 60 s y `HTTP Request2` respondió `ok`: **el reintento funcionó con datos reales**.
- La carpeta `Inspecciones_Pendientes` estaba vacía. `Hay_Imagenes_Pendientes` tomó la rama falsa y se enviaron **reales** el Gmail y el Telegram "sin inspecciones pendientes" (B4 real).
- `Leer_Reportes_NC` leyó la hoja real. `Embeddings_Transformer_HF` respondió **HTTP 401 "Invalid username or password."**, así que la credencial Header Auth de Hugging Face no es válida. `Clasificar_NLP_Python` aplicó el respaldo por reglas y lo informó (`transformer_ejecutado: false`, `metodo_usado_operacion: Reglas`). El flujo no se cayó.
- `Integracion_3_Modelos` devolvió 0 ítems (sin imágenes). No hubo llamada al LLM ni registro vacío.
