# VisionGuard Industrial — Informe técnico final (Hito 2)

**Curso:** IA Generativa para la Gestión Industrial · **Caso A:** control de calidad en manufactura (fundición de piezas metálicas)
**Versión del sistema:** v2.2 · **Fecha:** 14 de noviembre de 2026
**Alcance:** prototipo académico. Las imágenes provienen de un conjunto público; la serie temporal y los reportes de no conformidad son **simulados** con supuestos explícitos. Ninguna cifra de este informe corresponde a una planta real.

---

## Resumen ejecutivo

VisionGuard apoya al **inspector de calidad** en la decisión que toma en cada turno: **apartar una pieza, enviarla a revisión o continuar con la validación según protocolo**, y priorizar la línea de producción que debe revisarse. El sistema integra tres modelos y un LLM en un flujo n8n que corre solo tres veces al día:

| Componente | Qué hace | Resultado verificable (datos de prueba no usados para ajustar) |
|---|---|---|
| ResNet18 (CNN, ONNX, API Python) | Clasifica la foto de la pieza: Correcta / Defectuosa | Accuracy 97,76 % vs 69,51 % de un umbral simple (715 imágenes, Hito 1) |
| GRU (Keras, API Python) | Pronostica la tasa de defectos de mañana por línea | MAE 1,767 pp en prueba: **no supera** al promedio móvil (1,617) ni al SES (1,567) |
| Transformer NLP (MiniLM multilingüe) | Clasifica reportes de no conformidad por causa | F1 macro 0,347 vs 0,515 de las reglas fijas: **el Transformer no gana** (ver §4.3) |
| GPT-4o mini | Integra los tres resultados y redacta diagnóstico y recomendación en JSON | 11 campos validados, control numérico anti-alucinación, respaldo determinista |
| Control humano | Aprobación por Gmail de cada pieza antes de la acción | Decisión, fecha y estado se guardan en Sheets y se notifican por Gmail y Telegram |

Con supuestos explícitos, el **ROI del año 1 del escenario base es 36,5 %** (recuperación en 6,7 meses). El escenario conservador da 5,5 % y el optimista 260 %. El punto de equilibrio está en 4,1 horas de inspector ahorradas al mes.

---

## 1. Problema, usuario, decisión e indicador

**Contexto.** En una fundición de piezas (rodetes, carcasas, bridas), la inspección visual es manual y su registro se hace al final del turno. Los defectos de fundición (porosidad, rechupes, inclusiones) que llegan al cliente generan reproceso, flete y reclamos. En el conjunto público usado, el 57 % de las imágenes son piezas defectuosas (4.211 de 7.348; 453 de 715 en el test). Esa proporción está muy por encima de la de una planta real; ver §2.3.

| Elemento | Definición |
|---|---|
| Usuario | Inspector de calidad del turno; escalamiento al jefe de calidad |
| Decisión recurrente | Por pieza: apartar / revisión manual / continuar con validación. Por turno: qué línea revisar primero |
| Frecuencia | Cada turno (07:00, 15:00 y 23:00); una decisión por pieza fotografiada |
| Opciones | APROBAR la acción propuesta, RECHAZARLA (pide revisión adicional) o no responder (se escala tras 8 h) |
| Indicador de negocio | **Tasa de defectos por línea (%)** y **piezas defectuosas que llegan al cliente (escapes/mes)** |
| Línea base | Tasa media simulada: L1 4,56 %, L2 6,59 %, L3 7,57 %. Falsos negativos de ResNet18: 13/453 = 2,87 % |
| Cálculo | Tasa = piezas defectuosas / piezas inspeccionadas por línea y día. Escapes = defectuosas aprobadas que reclama el cliente |
| Indicador de proceso | Horas de inspector dedicadas a registrar e informar (se busca reducirlas) |

## 2. Datos

### 2.1 Origen

| Fuente | Tipo | Origen | Período / volumen | Variables |
|---|---|---|---|---|
| Imágenes de piezas | No estructurado | Público: *Casting product image data for quality inspection* (Kaggle) | 7.348 imágenes; split 5.306 / 1.327 / 715 | píxeles 300×300, clase ok/def |
| Tasa diaria de defectos | Estructurado (serie) | **Simulado**, semilla 20261112 | 180 días (1-may a 27-oct-2026) × 3 líneas = 540 filas | piezas inspeccionadas, defectuosas, tasa |
| Reportes de no conformidad | Texto | **Simulado**, semilla 20261114 | 110 reportes: 50 referencia, 40 prueba, 20 operación | texto, rol, causa (5 clases) |
| Historial operativo | Estructurado | Generado por el flujo | 1 fila por pieza y día | 27 columnas en `Analisis_Integrado` |

**Supuestos de la simulación de la serie:** tasa base 4,5 %, 6,0 % y 7,5 % por línea; estacionalidad semanal de ±0,8 pp; ruido uniforme ±1,2 pp; **cambio de nivel de +1,8 pp en L2 desde el día 120** (un desajuste de proceso); piezas/día entre 180 y 320; defectuosas ~ Binomial(n, tasa).

**Supuestos de los reportes NC:** 5 causas balanceadas (materia prima, ajuste de proceso, herramienta/molde, operación manual, medición). La mitad usa vocabulario técnico y la otra mitad paráfrasis coloquiales sin las palabras clave, como escribiría un operador. Hay frases distractoras en el 25 % de los reportes. **Las frases de los reportes de prueba no aparecen en los de referencia**, para que no haya fuga de información.

### 2.2 Limpieza y validación dentro del flujo

| Regla | Dónde | Acción ante dato inválido |
|---|---|---|
| Imagen ≤ 10 MB y decodificable | API ResNet18 (`app.py`) | HTTP 413/400; el flujo continúa con las demás imágenes y emite la alerta `ERROR_INFERENCIA_IMAGEN` |
| Clase ∈ {Correcta, Defectuosa}; confianza numérica | `Integracion_3_Modelos` | La imagen se excluye del análisis |
| Defectuosa sin revisión exigida por la API | `Integracion_3_Modelos` | Se fuerza la revisión humana y se emite la alerta `INCONSISTENCIA_API` |
| 7 tasas finitas en [0, 1]; línea ∈ {L1, L2, L3} | API GRU (`/pronosticar`) | HTTP 422 |
| Sin nulos, sin duplicados (fecha, línea), defectuosas ≤ inspeccionadas | `comparar_series.py`, notebook GRU | Se detiene con error explícito |
| Reporte NC sin id o sin texto, id duplicado, texto > 600 caracteres | `Preparar_Textos_NLP` | Se descarta o se recorta; queda en `descartados_validacion` |
| Vectores de embeddings con la dimensión y la cantidad esperadas | `Parsear_Embeddings` | Solo se usan las reglas y se emite `NLP_TRANSFORMER_NO_DISPONIBLE` |
| La misma imagen el mismo día | `Evitar_Notificaciones_Duplicadas` (clave `INTEGRADO\|archivo\|fecha`) | No se vuelve a registrar ni a notificar |

### 2.3 Limitaciones de los datos y su efecto

- **Imágenes:** un solo producto (impulsor de bomba), vista frontal, iluminación controlada. Fuera de ese dominio la confianza de ResNet18 no es confiable, y por eso toda confianza < 90 % exige revisión.
- **Serie:** es simulada y su estructura es conocida. Con solo 81 puntos de prueba, diferencias de MAE menores a ~0,1 pp no son concluyentes. El endpoint `/pronosticos-demo` siempre pronostica el 28-oct-2026, así que el historial GRU de producción repite valores. Es una demostración, no un monitoreo.
- **Texto:** los reportes NC son plantillas simuladas en español neutro. Las métricas NLP sirven para comparar métodos entre sí, no para estimar el desempeño con reportes reales, que traen faltas de ortografía, jerga y causas mixtas.
- **Desbalance:** el test de imágenes tiene 63 % de piezas defectuosas, más que una planta real (≈5-8 %). En producción la precisión de la clase Defectuosa sería menor.

## 3. Arquitectura del flujo (n8n Cloud, `VisionGuard v2.2 - Hito 2 FINAL`, 61 nodos)

```
Schedule (07/15/23 h) → Config (URLs, destinatarios, umbrales)
 ├─ /health ResNet18 ─(falla)→ espera 60 s → /health ─(falla)→ Gmail + Telegram "API no disponible"
 │    └─ Drive: Inspecciones_Pendientes ─(vacía)→ Gmail + Telegram "sin pendientes"
 │         └─ Descargar → POST /predict (ResNet18 ONNX, Python) ─┐
 ├─ /health GRU → espera 90 s → GET /pronosticos-demo (GRU Keras, Python) → Resumen_GRU ─┤ (+ historial Pronosticos_GRU)
 ├─ Sheets: Analisis_NLP (casos almacenados) ─────────────────────────────────────────────┤
 └─ Sheets: Reportes_NC → Preparar → HF embeddings (Transformer) → Parsear → Clasificar_NLP_Python ─┤
                                                                                        Merge (4)
 → Integracion_3_Modelos (resumen + alertas) → GPT-4o mini (JSON, 3 reintentos)
 → Validacion_Seguridad_Final (estructura, seguridad, anti-alucinación, respaldo)
 → Preparar_Registro → Dedupe → Sheets Analisis_Integrado → Loop por pieza:
      ├─ Gmail informe (con botón al panel) → mover imagen a Inspecciones_Procesadas
      ├─ Telegram informe (con enlace al panel)
      └─ Gmail APROBAR/RECHAZAR (espera ≤ 8 h) → registrar decisión en Sheets → Gmail + Telegram decisión final → siguiente pieza
Workflow aparte: Error Trigger → Gmail + Telegram con nodo y mensaje del error
```

**Código Python propio:** (1) API ResNet18: preprocesamiento, inferencia ONNX, softmax, regla de revisión (`python/apis/resnet18_api/app.py`). (2) API GRU: validación, normalización, inferencia y promedio móvil (`python/apis/series_gru_api/app.py`). (3) **Nodo Code en Python dentro de n8n**, `Clasificar_NLP_Python`: centroides de embeddings, similitud coseno, reglas, accuracy y F1 macro, escrito sin `import` para que corra en el runner nativo (`python/n8n_nodes/clasificar_nlp.py`). (4) Scripts de evaluación offline (`python/series`, `python/nlp`, `python/negocio`).

## 4. Modelos y comparación con la alternativa simple

### 4.1 Imágenes — ResNet18

ResNet18 preentrenada en ImageNet y ajustada 5 épocas. Se eligió por sus conexiones residuales, que transfieren bien con pocos datos, y porque su tamaño (44,7 MB en ONNX) permite inferir en CPU en el plan gratuito de Render.

| Métrica (test, 715 imágenes) | Umbral simple | ResNet18 |
|---|---|---|
| Accuracy | 69,51 % | **97,76 %** |
| Precisión Defectuosa | 78,18 % | 99,32 % |
| Recall Defectuosa | 71,96 % | 97,13 % |
| F1 Defectuosa | 74,94 % | 98,21 % |
| Falsos negativos | — | 13 de 453 (2,87 %) |

**Comparación con otros modelos preentrenados (exigida en el Hito 2):** el notebook `VisionGuard_Hito2_Comparaciones_Colab.ipynb` (parte A) reevalúa el **mismo ONNX desplegado** sobre las 715 imágenes y ajusta **EfficientNet-B0** y **MobileNetV3-Large** con la misma receta, partición y semilla. Reporta accuracy, F1, falsos negativos, latencia en CPU y una prueba de McNemar pareada. **Estado: listo, no ejecutado** (necesita GPU de Colab y descargar el dataset). Criterio de elección definido antes de ver los resultados: menos falsos negativos, luego F1 de la clase Defectuosa, luego latencia en CPU.

### 4.2 Serie temporal — GRU vs métodos clásicos

GRU de 24 unidades con ventana de 7 días y one-hot de línea (2.473 parámetros). La partición es cronológica (70/15/15 por fecha) y la normalización usa solo datos de entrenamiento. Los modelos clásicos se ajustan solo con entrenamiento. **Las predicciones GRU de prueba se obtuvieron consultando la API desplegada**, 162 llamadas a `/pronosticar`, y reproducen el notebook: MAE 1,7666 vs 1,7668 pp.

| Modelo (1 día adelante, pp) | MAE validación | MAE prueba | RMSE prueba |
|---|---|---|---|
| SES | 1,487 | **1,567** | 1,904 |
| Holt-Winters semanal | **1,407** | 1,599 | 1,979 |
| Promedio móvil 7 días | 1,571 | 1,617 | 1,963 |
| Regresión (media 7 lags + día de semana) | 1,474 | 1,717 | 2,195 |
| Holt | 1,692 | 1,746 | 2,137 |
| **GRU** | 1,546 | 1,767 | 2,262 |
| Ingenuo | 1,785 | 2,054 | 2,526 |

**Discusión (Navaja de Occam):** el GRU le gana al promedio móvil en validación, que es la única comparación que hacía la API, pero **pierde en prueba contra cuatro métodos clásicos**. La serie es corta y ruidosa y su estructura (nivel + semana) la capturan bien SES y Holt-Winters. Por eso el sistema usa el GRU como componente demostrativo, muestra siempre el promedio móvil al lado y **alerta cuando ambos difieren ≥ 1,5 pp**. Para producción se recomendaría Holt-Winters, que fue el mejor en validación. **Detección de cambio de nivel:** un CUSUM (k = 0,5σ, h = 5σ) detecta el desajuste simulado de L2 cuatro días después de ocurrido (día 124 vs 120).

### 4.3 Texto — Transformer vs reglas

Modelo: `paraphrase-multilingual-MiniLM-L12-v2`, un encoder tipo BERT de 12 capas con auto-atención y embeddings de 384 dimensiones que soporta español. Método: el centroide de los 50 reportes de referencia por causa y la asignación por similitud coseno. Las reglas son palabras clave fijadas antes de generar los textos.

| Método (40 reportes de prueba) | Accuracy | F1 macro | Sin clasificar |
|---|---|---|---|
| **Reglas fijas** | **42,5 %** | **0,515** | 15 / 40 |
| Transformer MiniLM (centroide) | 37,5 % | 0,347 | 0 / 40 |
| *Híbrido (post hoc, exploratorio)* | *55,0 %* | *0,544* | *0 / 40* |

Ejecutado localmente el 14-nov-2026 en CPU con `evaluar_nlp.py`, que es el mismo método que corre el nodo Python del flujo. Resultado en `python/nlp/resultados_nlp.json`.

**Discusión (Navaja de Occam): el Transformer no supera a las reglas.** Hay tres causas probables:
1. El contexto común de todos los reportes ("Línea L2, rodete: no conformidad detectada en…") ocupa gran parte del texto y acerca los embeddings entre causas distintas.
2. Cada causa tiene solo 3 frases distintas en el conjunto de referencia, así que su centroide representa poca variedad.
3. MiniLM es un modelo general, no entrenado en vocabulario de fundición.

Las reglas aciertan cuando hay palabra clave, pero dejan sin clasificar 15 reportes. En esos 15, el Transformer acierta 5.

El híbrido (reglas primero y Transformer solo si las reglas no clasifican) llega a F1 0,544. Se diseñó **después de ver la prueba**, por lo que se informa como hipótesis y no como métrica final.

**Consecuencia en el flujo:** para los reportes nuevos, `Clasificar_NLP_Python` usa el método con mejor F1 medido en cada corrida; hoy son las reglas, y queda registrado en `metodo_usado_operacion`. El Transformer sigue ejecutándose y midiéndose en cada turno.

**Mejoras para validar con datos reales:**
- quitar el contexto común antes de calcular los embeddings;
- usar más reportes de referencia por causa;
- ajuste fino (fine-tuning) con reportes reales etiquetados.

## 5. LLM: prompt, salida estructurada y control de alucinaciones

**Prompt (`LLM_Integrado`, completo en el JSON del flujo):** rol de especialista en calidad y riesgo; contexto del prototipo y de los datos simulados; el **resumen** generado por `Integracion_3_Modelos`, que contiene clasificaciones, confianzas, pronósticos, métricas NLP y alertas, nunca la tabla cruda; 30 reglas numeradas (no inventar defectos, causas ni cifras; distinguir predicción de observación; no afirmar tendencias sin serie histórica; tratar el NLP como antecedente; nunca aprobar automáticamente; mencionar cada alerta; toda cifra debe existir en los datos); y un formato JSON fijo de 11 claves.

**Validación posterior (`Validacion_Seguridad_Final`):**
1. Parseo tolerante (acepta respuestas envueltas en ```json```).
2. Estructura: 11 campos y 7 textos no vacíos.
3. Reglas deterministas: la prioridad alta si hay una pieza defectuosa, `requiere_revision_humana = true` y `aprobacion_automatica = false` se **corrigen** si el LLM las viola, y la respuesta queda marcada como `LLM_CORREGIDO`.
4. **Anti-alucinación numérica:** cada cifra del texto se contrasta con todos los números de la entrada (incluidas las conversiones a %). Las cifras no respaldadas se listan, se marca `alucinacion_sospechada` y se avisa en el correo y en el tablero.
5. Se detectan frases de aprobación sin negación.
6. Si el JSON es inválido o el nodo LLM falla tras 3 reintentos, se genera un **análisis determinista de respaldo** con prioridad alta y el flujo no se cae.

**Ejemplo de salida (prueba unitaria 4, JSON del LLM truncado):**

```json
{"fuente_analisis": "RESPALDO_DETERMINISTA", "prioridad": "alta",
 "diagnostico": "Analisis de respaldo (sin LLM valido). ResNet18: 1 imagen(es), 1 defectuosa(s): VG_T4.jpeg Defectuosa (97.00 %). GRU simulado: mayor pronostico en L3 (7.89 %). ...",
 "recomendacion": "Apartar las piezas defectuosas e inspeccionarlas manualmente. No aprobar automaticamente.",
 "requiere_revision_humana": true, "aprobacion_automatica": false,
 "controles_seguridad": {"json_valido": false, "fallas_llm": ["JSON invalido del LLM."], "alucinacion_sospechada": false}}
```

## 6. Automatización, notificaciones y control humano

- **Disparo:** el Schedule corre en los tres turnos sin intervención.
- **Robustez:**
  - Reintentos en las APIs, Sheets, Gmail, Telegram y el LLM.
  - Espera de 60/90 s para el arranque en frío de Render.
  - Rutas de error en tres situaciones: API caída, carpeta vacía e imagen corrupta.
  - Respaldo cuando el JSON del LLM es inválido.
  - Workflow de errores aparte que avisa por Gmail y Telegram.
- **Gmail siempre:** informe por pieza, aviso de turno sin pendientes, aviso de API caída, solicitud de aprobación, decisión final y errores.
- **Telegram:** los mismos eventos, en un formato breve y legible en el móvil.
- **Enlace al tablero:** todos los avisos llevan el enlace (`Config.dashboard_url`).
- **Punto de control humano:**
  - Un correo APROBAR/RECHAZAR por pieza (bucle `Loop_Inspecciones`).
  - Si no hay respuesta en 8 h, el estado queda `SIN_RESPUESTA_HUMANA_ESCALAR` y la pieza sigue apartada.
  - La decisión, su fecha y el estado se escriben en `Analisis_Integrado`.
  - **Una pieza defectuosa nunca se aprueba automáticamente.**
- **Sin duplicados:** la deduplicación ocurre **antes** de guardar, así que una nueva ejecución no pisa una decisión humana ya registrada.
- **Imágenes procesadas:** se mueven a `Inspecciones_Procesadas`.

## 7. Tablero

`Dashboard` en Google Sheets, creado por `dashboard/VisionGuard_Dashboard_Sheets.gs`:

- **12 KPIs**, entre ellos la tasa de defectos, las pendientes, las autorizadas o rechazadas, las respuestas de respaldo, las cifras no respaldadas y el ROI.
- **Filtros interactivos:** clasificación, prioridad y fecha desde.
- **9 gráficos:**
  - clasificación;
  - prioridad;
  - inspecciones por día;
  - confianza en el tiempo;
  - decisiones humanas;
  - GRU por línea en el tiempo;
  - MAE de las series;
  - NLP;
  - ROI.
- **Registro** de las últimas 15 recomendaciones del LLM.
- **Tablas de evidencia** de los modelos.

Se complementa con el dashboard de Colab existente (`notebooks/VisionGuard_Dashboard_Colab.ipynb`). Se eligió Sheets porque es publicable y su enlace se abre desde el móvil al tocar el aviso.

## 8. Evaluación de negocio (estimación académica)

**Supuestos:**
- Inspector a 8.500 CLP/h; ingeniero a 25.000 CLP/h.
- Escape de una pieza defectuosa: 60.000 CLP (reproceso, flete y reclamo).
- Costos de operación al año:
  - n8n Starter;
  - GPT-4o mini;
  - 2 APIs en Render Starter;
  - Hugging Face PRO;
  - 4 h/mes de mantención.
  - Total: **1.797.600 CLP/año**.
- Implementación: 60 h, **1.500.000 CLP** (una vez).

| Escenario | Horas ahorradas/mes | Escapes evitados/mes | Beneficio anual | ROI año 1 | ROI año 2 | Recuperación |
|---|---|---|---|---|---|---|
| Conservador | 20 | 2 | 3.480.000 | 5,5 % | 93,6 % | 10,7 meses |
| **Base (equipo)** | 15,9 | 4 | 4.501.224 | **36,5 %** | 150,4 % | 6,7 meses |
| Optimista | 60 | 8 | 11.880.000 | 260,3 % | 560,9 % | 1,8 meses |

El 36,5 % del equipo se conserva como escenario base. Como sus supuestos no estaban documentados, aquí se calculó qué los reproduce: con 4 escapes evitados al mes hacen falta **≈ 15,9 h/mes** de registro e informe ahorradas, unos 10 minutos por turno. Es plausible, pero **debe validarse midiendo el tiempo real de registro manual**. **Riesgos económicos:**
- Cada falso negativo (2,87 %) es un escape que **resta** beneficio.
- Los costos de API escalan con el volumen de imágenes.
- Las horas "ahorradas" solo son beneficio si se reasignan a otra tarea.
- El ROI es sensible al costo por escape, que es el supuesto más incierto.

## 9. Riesgos, sesgos y ética

| Riesgo | Efecto | Mitigación implementada |
|---|---|---|
| Falso negativo de ResNet18 | Pieza defectuosa sigue el flujo | Nunca hay aprobación automática; revisión humana obligatoria para toda pieza; confianza < 90 % ⇒ alerta |
| Alucinación del LLM | Cifras, causas o aprobaciones inventadas | Recibe solo el resumen; 30 reglas; control numérico y de frases; respaldo determinista; la clasificación del modelo prevalece |
| Deriva de dominio (otra cámara, otra pieza) | Confianza alta pero errónea | Limitación documentada; se recomienda reentrenar con fotos de la planta |
| Sesgo de los datos simulados | Métricas optimistas | Datos marcados `SIMULADO_ACADEMICO_NO_REAL` en todo el flujo y en los avisos |
| Datos sensibles | Exposición de credenciales o correos | Export público sin credenciales, correo, chat ni IDs; tokens en el gestor de credenciales de n8n. **La clave de servicio de Google Cloud usada antes se considera expuesta y debe revocarse** |
| Automatización sin respuesta humana | La decisión se dilata | Límite de 8 h ⇒ `SIN_RESPUESTA_HUMANA_ESCALAR`, notificado por Gmail y Telegram |
| Dependencia de servicios gratuitos | Caída del flujo | Health checks, reintentos y workflow de errores |

## 10. Pruebas realizadas (reproducibles)

- **15/15 pruebas unitarias** de los nodos Code con `node pruebas/harness_nodos.js`. Cubren:
  - pieza defectuosa y pieza correcta;
  - el LLM que intenta aprobar;
  - JSON inválido y error del LLM;
  - cifras inventadas y frase de aprobación sin negación;
  - ausencia de imágenes e imagen corrupta;
  - NLP sin token;
  - dos imágenes por ejecución;
  - respuesta envuelta en markdown;
  - deduplicación de reportes.
- El **nodo Python** da la misma salida que su gemelo JavaScript (`probar_nodo_python.py`).
- **Verificación estática** del workflow:
  - conexiones válidas;
  - todas las expresiones compilan;
  - el export público no contiene credenciales ni datos personales (`verificar_workflow.js`).
- **APIs en vivo** (14-nov-2026):
  - `/health` de ResNet18 responde `ok`;
  - `/pronosticos-demo` y `/pronosticar` del GRU responden;
  - se hicieron 162 llamadas para la evaluación.
- **Pendiente de evidencia en n8n:** tres ejecuciones completas con imágenes distintas y capturas de Gmail y Telegram (guía en `docs/PLAN_PRUEBAS_Y_EVIDENCIAS.md`).

## 11. Limitaciones

- La serie temporal y el texto son simulados.
- El endpoint GRU de demostración es estático.
- La comparación entre modelos de imagen está pendiente de ejecución en Colab.
- Las métricas NLP se calcularon con reportes simulados.
- No hay calibración probabilística de ResNet18.
- El LLM analiza todas las imágenes de una ejecución en una sola llamada; con muchas imágenes por turno convendría una llamada por pieza.
- El ROI es una estimación académica.
