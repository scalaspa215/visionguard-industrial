# VisionGuard Industrial — Workflow de automatización (plantilla pública)

Este archivo acompaña a `VisionGuard_Workflow_Publico_Seguro.json` y documenta el flujo exportado de n8n. Se ha conservado la estructura original de **17 nodos y sus conexiones**, pero se han eliminado identificadores personales y referencias privadas. El workflow está **desactivado** por defecto y **no puede ejecutarse sin configurarlo**.

## Qué hace

1. Un `Schedule Trigger` comprueba periódicamente el estado de una API de inferencia.
2. Si el Health Check falla, espera 60 segundos y vuelve a comprobarlo. Si vuelve a fallar, prepara un aviso crítico por Gmail.
3. Si la API responde correctamente, busca imágenes en `Inspecciones_Pendientes` (Google Drive), las descarga y las envía a `/predict`.
4. El servicio de visión devuelve clasificación y confianza; un LLM genera un diagnóstico estructurado en JSON.
5. Guarda resultados en Google Sheets. Si la inspección es defectuosa o requiere revisión humana, envía un correo de aviso.
6. Mueve la imagen a `Inspecciones_Procesadas` tanto en la ruta con aviso como en la ruta sin aviso.

## Configuración necesaria al importar en n8n

- **API de inferencia:** sustituir `https://YOUR-INFERENCE-API.example.com` en `HTTP Request`, `HTTP Request1`, `HTTP Request2` y en el mensaje de alerta crítica.
- **Google Drive:** reconectar las credenciales OAuth; crear o seleccionar las carpetas `Inspecciones_Pendientes` y `Inspecciones_Procesadas`. Reemplazar `REPLACE_WITH_PROCESSED_FOLDER_ID` en los dos nodos `Move file`. Revisar que la búsqueda de la carpeta pendiente elija la carpeta correcta.
- **Google Sheets:** reconectar las credenciales OAuth y reemplazar `REPLACE_WITH_YOUR_SPREADSHEET_ID`. Seleccionar la pestaña correcta y adaptar el mapeo de columnas a la hoja real.
- **Gmail:** reconectar las credenciales y cambiar el destinatario de ejemplo `inspector@example.com` en ambos nodos de envío.
- **Modelo de lenguaje:** seleccionar/reconectar una credencial compatible para el nodo `Message a model` (configurado para GPT-4o mini).
- **Activación:** verificar manualmente el circuito completo antes de activar el `Schedule Trigger` o publicar el flujo.

## Consideraciones técnicas

- La exportación incluye un **Append Row** sin mecanismo de deduplicación. Reejecutar una imagen o reintentar después de un fallo ambiguo de Google Sheets puede generar registros duplicados. Una mejora recomendada es usar un identificador único de archivo/inspección y hacer una búsqueda previa o un upsert.
- El mapeo original de columnas tiene espacios en dos claves (`fecha_hora ` y ` archivo`). Revisa los encabezados y elimina esa inconsistencia en la hoja y en los campos del nodo cuando adaptes la plantilla.
- El modelo genera una **recomendación**, no una aprobación industrial definitiva; las predicciones inciertas requieren revisión humana según el procedimiento de calidad.
- El correo de estado crítico está escrito para el escenario en que ambos chequeos fallan. Una respuesta HTTP 404 de una ruta de prueba puede usarse para simular el fallo sin apagar el servidor real.
- No se incluyen imágenes ni datos de inspección. La validación de cada integración debe realizarse en el entorno del usuario.

## Seguridad de la plantilla

La copia pública elimina correos personales, identificadores de OAuth, IDs de documentos/carpetas, IDs de instancia, IDs internos de workflow y de webhook, y reemplaza la URL específica de implementación por una dirección de ejemplo. No subas al repositorio público el archivo de exportación original ni archivos `.env`, tokens o credenciales reales.
