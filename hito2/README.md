# VisionGuard Industrial · Hito 2 (v2.2)

Sistema de apoyo a la decisión para el control de calidad de piezas metálicas fundidas. Integra **ResNet18** (imagen), **GRU** (serie temporal), un **Transformer NLP** (reportes de no conformidad) y **GPT-4o mini**, orquestados en **n8n**, con aprobación humana por pieza, notificaciones por Gmail y Telegram y un tablero en Google Sheets.

> Prototipo académico. La serie temporal y los reportes NC son **simulados** (supuestos en `docs/INFORME_TECNICO_HITO2.md` §2). Ninguna pieza se aprueba automáticamente.

## Estructura

```
n8n/          workflow v2.2 (IMPORTAR = con referencias a tus credenciales; PUBLICO = anonimizado),
              Error Handler y build_workflow_v22.py (genera ambos desde el respaldo v2.1)
python/
  apis/       resnet18_api (FastAPI + ONNX) · series_gru_api (FastAPI + Keras)
  n8n_nodes/  código de cada nodo Code del flujo (JS comentado + nodo Python)
  series/     comparar_series.py → GRU (API real) vs 6 métodos clásicos + CUSUM
  nlp/        generador de reportes NC, reglas, evaluación Transformer vs reglas
  negocio/    roi_visionguard.py → escenarios, sensibilidad, recuperación
dashboard/    VisionGuard_Dashboard_Sheets.gs (tablero interactivo en Sheets)
notebooks/    entrenamiento GRU · comparaciones (Colab GPU) · dashboard Colab
pruebas/      15 pruebas unitarias de nodos, paridad Python/JS, verificación del workflow
docs/         informe técnico · matriz de cumplimiento · guía n8n · plan de pruebas · guion
```

## Resultados principales (datos de prueba no usados para ajustar)

| Modelo | Alternativa simple | Resultado |
|---|---|---|
| ResNet18 | Umbral simple | Accuracy 97,76 % vs 69,51 % (715 imágenes) |
| GRU | Promedio móvil 7 d / SES | MAE prueba 1,767 vs 1,617 / 1,567 pp → **el GRU no gana** |
| Transformer MiniLM | Reglas fijas | F1 macro 0,347 vs 0,515 → **ganan las reglas** (40 reportes simulados) |
| ROI (estimado) | — | Año 1: 5,5 % / **36,5 %** / 260 % (conservador / base / optimista) |

## Reproducir

```bash
python python/series/comparar_series.py      # usa la API GRU desplegada (o --sin-api)
python python/nlp/generar_reportes_nc.py && python python/nlp/evaluar_nlp.py
python python/negocio/roi_visionguard.py
node pruebas/harness_nodos.js && python pruebas/probar_nodo_python.py && node pruebas/verificar_workflow.js
python n8n/build_workflow_v22.py             # regenera los JSON del flujo
```

Puesta en marcha: `docs/GUIA_IMPLEMENTACION_N8N.md`.

## Seguridad
- Los exports públicos no contienen credenciales, correos, chat IDs ni IDs de hojas (lo verifica `pruebas/verificar_workflow.js`).
- Los tokens (Hugging Face, Telegram, Google) viven solo en *Credentials* de n8n.
- La clave de servicio de Google Cloud usada antes se considera **expuesta** y debe revocarse.
