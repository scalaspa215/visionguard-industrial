# VisionGuard Industrial
### AI-Powered Industrial Quality Control System

**Versión:** 1.4 — Telegram Integration & Industrial Safety Validation 
**Proyecto académico:** IA Generativa para la Gestión Industrial  
**Estado:** Prototipo funcional validado mediante pruebas de integración

## 1. Descripción del proyecto

VisionGuard Industrial es un sistema de inspección automatizada de calidad para piezas metálicas que integra visión artificial, inteligencia artificial generativa y automatización de procesos.

El sistema utiliza una red neuronal ResNet18 para clasificar imágenes de piezas metálicas, una API desarrollada en Python para realizar inferencias y GPT-4o mini para generar diagnósticos industriales estructurados.

Mediante n8n, el sistema automatiza la recepción de imágenes, clasificación, generación de recomendaciones, registro de inspecciones y notificaciones.

**Objetivo:** apoyar las decisiones de control de calidad, mejorar la trazabilidad de las inspecciones y reducir tareas manuales repetitivas sin eliminar la supervisión humana.

## 2. Arquitectura tecnológica

| Componente | Tecnología |
|---|---|
| Clasificación visual | ResNet18 |
| Formato de inferencia | ONNX |
| Backend | Python |
| Infraestructura API | Render |
| IA generativa | GPT-4o mini |
| Automatización | n8n Cloud |
| Almacenamiento | Google Drive |
| Registro histórico | Google Sheets |
| Notificaciones | Gmail |
| Control de versiones | GitHub |

### Flujo de funcionamiento

1. n8n inicia una inspección mediante un disparador programado.
2. El sistema verifica la disponibilidad de la API en Render.
3. Recupera imágenes desde Google Drive.
4. Envía cada imagen a ResNet18 para su clasificación.
5. GPT-4o mini genera un diagnóstico, prioridad, recomendación y justificación.
6. Un nodo JavaScript valida las reglas críticas de seguridad.
7. Google Sheets almacena los resultados.
8. Gmail envía alertas cuando corresponde.
9. Google Drive mueve la imagen a la carpeta de inspecciones procesadas.

## 3. Dataset y entrenamiento

**Dataset:** Casting Product Image Data for Quality Inspection, disponible en Kaggle.

El conjunto utilizado contiene 7.348 imágenes de piezas metálicas, divididas en dos clases: correctas y defectuosas.

| Conjunto | Imágenes |
|---|---:|
| Entrenamiento | 5.306 |
| Validación | 1.327 |
| Prueba | 715 |
| **Total** | **7.348** |

Se entrenó un modelo baseline ResNet18 durante cinco épocas, utilizando una partición estratificada para preservar la distribución de clases.

## 4. Resultados del modelo

Resultados obtenidos sobre el conjunto de prueba independiente de 715 imágenes:

| Métrica | Resultado |
|---|---:|
| Accuracy | 97,76 % |
| Precision — defectuosa | 99,32 % |
| Recall — defectuosa | 97,12 % |
| F1-score — defectuosa | 98,21 % |

**Matriz de confusión:**

- Verdaderos negativos (TN): 259
- Falsos positivos (FP): 3
- Falsos negativos (FN): 13
- Verdaderos positivos (TP): 440

Estos resultados corresponden a una evaluación experimental sobre el dataset y no constituyen una certificación de funcionamiento industrial.

## 5. Inteligencia artificial generativa

GPT-4o mini recibe la clasificación, confianza, probabilidades y decisión sugerida por el modelo visual.

Genera una respuesta JSON estructurada con los siguientes campos:

- archivo
- clasificacion
- confianza
- diagnostico
- prioridad
- recomendacion
- justificacion
- requiere_revision_humana

La IA generativa no analiza directamente la imagen ni debe inventar características físicas que el modelo visual no haya identificado.

## 6. Seguridad industrial y supervisión humana

La versión 1.3 incorpora una validación determinista implementada mediante JavaScript en n8n.

**Reglas de seguridad:**

- Una pieza clasificada como defectuosa requiere revisión humana obligatoria.
- Toda pieza defectuosa recibe prioridad alta.
- Las piezas con incertidumbre conservan los requisitos de revisión indicados por la API.
- Ninguna predicción automatizada constituye una aprobación definitiva.
- La decisión final corresponde al responsable autorizado de control de calidad.

Estas reglas se aplican después de la respuesta generativa, evitando que una inconsistencia del modelo de lenguaje anule el requisito de revisión.

## 7. Automatización y trazabilidad

El flujo de n8n contiene 18 nodos funcionales, incluyendo:

- Verificación de disponibilidad de la API.
- Reintento de conexión y espera ante indisponibilidad.
- Procesamiento de imágenes.
- Inferencia mediante Python y ONNX.
- Diagnóstico mediante IA generativa.
- Validación de seguridad con JavaScript.
- Registro automático en Google Sheets.
- Notificaciones por Gmail.
- Movimiento de archivos en Google Drive.

## 8. Prueba integral de la versión 1.3

**Fecha:** 7 de noviembre de 2026  
**Archivo de prueba:** VG_TEST_008.jpeg

| Resultado | Valor |
|---|---|
| Clasificación | Defectuosa |
| Confianza | 95,28 % |
| Prioridad | Alta |
| Revisión humana | Sí |
| Notificación Gmail | Exitosa |
| Registro Google Sheets | Exitoso |
| Movimiento Google Drive | Exitoso |

La prueba confirmó el funcionamiento integrado del flujo, incluyendo la validación obligatoria de revisión humana para piezas defectuosas.

## 9. Organización del repositorio

- `visionguard_api/`: implementación de la API de inferencia y componentes asociados al modelo.
- `VisionGuard_Workflow_v1.3.json`: versión pública del flujo de automatización.
- `VisionGuard_Workflow_Publico_Seguro.json`: respaldo público anterior del workflow.
- `README_VisionGuard_Workflow.md`: documentación complementaria de la automatización.
- `README.md`: documentación general del proyecto.

Los archivos públicos del workflow deben importarse utilizando credenciales propias y configurarse con identificadores de recursos autorizados antes de ejecutarlos.

## 10. Limitaciones y próximos desarrollos

La solución corresponde a un prototipo académico y requiere validación adicional antes de utilizarse para decisiones reales de producción.

Entre los desarrollos futuros se consideran:

- Evaluación de robustez con imágenes de nuevas condiciones industriales.
- Integración de técnicas Transformer y procesamiento de lenguaje natural.
- Tablero de indicadores y desempeño.
- Estimación del retorno económico y reducción potencial de mermas.
- Registro explícito de aprobaciones y rechazos humanos.
- Mejoras de monitoreo y continuidad operacional.

## 11. Conclusión

VisionGuard Industrial demuestra la integración funcional de aprendizaje profundo, inteligencia artificial generativa y automatización dentro de un proceso de control de calidad.

Los resultados experimentales de ResNet18 y las pruebas integrales de n8n respaldan la viabilidad técnica del prototipo, mientras que las validaciones deterministas mantienen la intervención humana como requisito de seguridad.

---

**VisionGuard Industrial v1.3 — Prototipo académico de control de calidad asistido por inteligencia artificial.**




## 12. Actualización v1.4 — Telegram Integration

**Fecha:** 8 de noviembre de 2026

### Nuevas funcionalidades
- Integración de Telegram Bot API mediante n8n.
- Envío automático de resultados de inspección por Telegram.
- Notificaciones Gmail para piezas defectuosas o que requieren revisión humana.
- Validación determinista de seguridad mediante JavaScript.
- Registro de inspecciones en Google Sheets.
- Movimiento automático de imágenes procesadas en Google Drive.

### Prueba de integración
Archivo: VG_TEST_009.jpeg

- Clasificación: Defectuosa.
- Confianza: 99,63 %.
- Prioridad: Alta.
- Revisión humana: Sí.
- Telegram: mensaje recibido correctamente.
- Gmail: correo de alerta recibido.
- Google Sheets: resultado registrado.
- Google Drive: imagen trasladada a Inspecciones_Procesadas.

### Workflow
El archivo `VisionGuard_Workflow_v1.4_PUBLICO_SEGURO.json` contiene la versión exportada para documentación y reproducción académica, sin credenciales privadas.

### Limitaciones
VisionGuard es un prototipo académico. Sus predicciones no sustituyen la inspección humana ni constituyen aprobaciones definitivas de calidad.

