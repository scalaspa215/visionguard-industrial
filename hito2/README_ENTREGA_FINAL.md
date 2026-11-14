# VisionGuard Industrial · Hito 2 · Entrega final

Prototipo académico de apoyo a la decisión para el control de calidad de piezas fundidas. Integra:
- **ResNet18** sobre las imágenes;
- **GRU** sobre la serie de defectos (simulada);
- un **Transformer MiniLM** sobre los reportes de no conformidad (simulados);
- **GPT-4o mini** para la recomendación.

Todo se orquesta en **n8n**, con aprobación humana por pieza, avisos por Gmail y Telegram y un tablero en Google Sheets.

> **Contexto de las cifras:**
> - Las métricas de los modelos vienen de evaluaciones offline sobre conjuntos de prueba. No miden el desempeño del flujo en producción.
> - La serie temporal y los reportes NC son **simulados**.
> - El ROI es una **estimación académica** con supuestos explícitos.

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `01_informe/` | Informe técnico final (Word, PDF y Markdown) |
| `02_workflow_n8n/` | Workflow `VisionGuard v2.2 - Hito 2 FINAL` exportado sin credenciales ni datos personales + script que lo genera |
| `03_error_handler/` | Workflow `VisionGuard v2.2 - Error Handler` (Error Trigger → Gmail + Telegram) |
| `04_codigo_python/` | APIs FastAPI (ResNet18 ONNX, GRU Keras), código de cada nodo Code (JS + nodo Python), scripts de evaluación de series, NLP y ROI |
| `05_notebooks/` | Entrenamiento del GRU, comparaciones en Colab (imágenes, NLP, series), dashboard Colab |
| `06_comparacion_modelos/` | Resultados y predicciones: series (7 modelos), NLP (Transformer vs reglas) |
| `07_negocio_roi/` | Escenarios, sensibilidad y gráfico del ROI |
| `08_evidencias/` | Ejecuciones n8n documentadas (pin data y reales), pruebas unitarias, plan de pruebas |
| `09_matriz_cumplimiento/` | Matriz R1–R11 con su estado |
| `10_presentacion_defensa/` | Presentación (.pptx) y guion de 15 min con preguntas individuales |
| `11_tablero/` | Apps Script del tablero en Sheets y guía de puesta en marcha |

## Reproducir los resultados (Python 3.11 con numpy, pandas y scipy)

```bash
python 04_codigo_python/python/series/comparar_series.py      # GRU vía API real + 6 modelos clásicos
python 04_codigo_python/python/nlp/evaluar_nlp.py             # reglas; Transformer requiere: pip install sentence-transformers
python 04_codigo_python/python/negocio/roi_visionguard.py
node   08_evidencias/pruebas/harness_nodos.js                 # 15 pruebas unitarias de los nodos Code
```

## Seguridad
- Los archivos no contienen contraseñas, tokens, claves privadas, correos ni IDs de hojas. Lo verifica un barrido automático al generar esta carpeta.
- Las credenciales viven solo en n8n.
- La clave de servicio de Google Cloud usada en una versión anterior (Streamlit) se considera **expuesta y debe revocarse** en Google Cloud Console.
