# Matriz de cumplimiento — Hito 2 (estado al 14-nov-2026)

**I** = implementado · **D** = demostrado con evidencia reproducible · **P** = pendiente (requiere acción humana)

## Requisitos R1–R11

| Req. | Exigencia | Implementación v2.2 | Estado | Avance | Evidencia |
|---|---|---|---|---|---|
| R1 LLM | JSON estructurado con recomendación | GPT-4o mini con 11 claves; validación, corrección, anti-alucinación y respaldo | I, D (unitario) · P (ejecución en vivo) | 90 % | `n8n_nodes/validacion_seguridad_final.js`, pruebas A1 1–7 y 12 |
| R2 Python | Código propio entregado | 2 APIs FastAPI + nodo Code Python en n8n + scripts de evaluación | I, D | 95 % | `python/apis/*`, `n8n_nodes/clasificar_nlp.py`, prueba A2 |
| R3 Serie | Pronóstico vs base simple; clásico vs DL | GRU vs 6 métodos clásicos con la misma partición; GRU vía API real; CUSUM | I, D | 90 % | `series/resultados_series.json` |
| R4 Imágenes | 2 modelos preentrenados comparados | ResNet18 desplegado; notebook con EfficientNet-B0 y MobileNetV3 + McNemar | I · P (correr Colab) | 70 % | `notebooks/VisionGuard_Hito2_Comparaciones_Colab.ipynb` (A) |
| R5 Transformer | Modelo de atención sobre texto industrial | MiniLM multilingüe + centroides en Python dentro del flujo; comparado con reglas (F1 0,347 vs 0,515: ganan las reglas, se discute) | I, D (offline) · P (token HF para el flujo) | 80 % | `nlp/resultados_nlp.json`; nodos `Embeddings_Transformer_HF` → `Clasificar_NLP_Python` |
| R6 Automatización | Corre sola y termina en acción | Schedule por turno, 61 nodos, reintentos, rutas de error, Error Handler | I, D (estático) · P (E2E) | 85 % | prueba A3; `PLAN_PRUEBAS` B1–B9 |
| R7 Contexto | Usuario, decisión, indicador con línea base | Inspector, 3 opciones, tasa de defectos y escapes, línea base | I, D | 95 % | Informe §1 |
| R8 Datos | Origen, limpieza, limitaciones | 3 fuentes documentadas, generadores reproducibles, 8 reglas de validación | I, D | 95 % | Informe §2, `generar_reportes_nc.py` |
| R9 Tablero | Interactivo y publicado; enlace en avisos | Dashboard en Sheets (filtros + 9 gráficos + log LLM) y Colab; enlace en todos los avisos | I · P (instalar y compartir) | 75 % | `dashboard/VisionGuard_Dashboard_Sheets.gs` |
| R10 Negocio y ética | ROI, riesgos, control humano | 3 escenarios, sensibilidad, recuperación; 7 riesgos mitigados; aprobación por pieza con timeout | I, D | 90 % | `negocio/roi_resultados.json`, Informe §8–9 |
| R11 Notificaciones | Gmail **siempre** + Telegram | Gmail y Telegram en informe, sin pendientes, API caída, decisión final y errores | I · P (capturas) | 85 % | nodos `Notificacion_*`, `Aviso_*`, `Telegram_API_Caida` |

## Retroalimentación del Hito 1 → acción

| Observación del profesor | Corrección |
|---|---|
| Faltaban el `.json` y el código de la API | Workflow v2.2 público + importable; código de las 2 APIs y de todos los nodos en `python/` |
| Una sola ejecución documentada | Plan B1–B9 con 3 casos mínimos y capturas (**P**) |
| Gmail solo condicional | Gmail en todo resultado y evento |
| El control post-LLM estaba en JavaScript | Se agregó un nodo Code **Python** dentro de n8n; los nodos JS ahora están comentados y probados |
| Notas de borrador en el informe | Informe final sin notas; lo pendiente va solo en esta matriz |
| Agregar datos estructurados y texto | Serie GRU (tasa diaria por línea) + reportes NC con un Transformer |
| Enlace al tablero en los avisos | `Config.dashboard_url` en los 9 avisos |

## Ponderación Hito 2 (estimación del equipo, no nota oficial)

| Componente | Peso | Avance hoy | Si se completan los pendientes |
|---|---|---|---|
| Integración técnica (R3–R6) | 25 % | 75 % | 95 % |
| Calidad de modelos y comparación | 15 % | 80 % | 95 % |
| LLM, RAG/contexto, alucinaciones | 15 % | 85 % | 95 % |
| Tablero | 10 % | 70 % | 95 % |
| Negocio, ROI, riesgos, control humano | 15 % | 90 % | 95 % |
| Informe final | 10 % | 85 % | 95 % |
| Defensa | 10 % | 50 % (guion listo) | depende del equipo |
| **Global ponderado** | 100 % | **≈ 78 %** | **≈ 95 %** |

## Pendientes que requieren intervención humana (en orden)
1. Revocar la clave de servicio de Google Cloud expuesta.
2. Importar la v2.2 y el Error Handler, asignar credenciales y crear el token de Hugging Face.
3. Instalar el Apps Script, pegar la URL del tablero en Config y compartir la hoja con el profesor (Lector).
4. Ejecutar el notebook de Colab (parte A, imágenes) y pegar sus cifras en el informe §4.1. La parte B (NLP) ya se ejecutó localmente.
5. Ejecutar B1–B3 (y ojalá B4–B9) con capturas de n8n, Gmail, Telegram y Sheets.
6. Subir la carpeta `hito2/` a GitHub (lo prepara este paquete; requiere tu autorización).
7. Ensayar el guion con cada integrante: hay preguntas individuales.
