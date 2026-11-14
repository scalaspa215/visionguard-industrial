# Guía de puesta en marcha — VisionGuard v2.2 (≈ 30 min)

> El workflow v2.1 **no se modifica**. La v2.2 se importa como un workflow nuevo. Si algo falla, se vuelve a activar la v2.1.
> Respaldo intacto: `original/workflow_backup_original.json`.

## 0. Seguridad (hacer primero)
1. **Revocar la clave de servicio de Google Cloud** que se usó con Streamlit: Google Cloud Console → IAM → Cuentas de servicio → Claves → eliminar. Se considera expuesta.
2. No pegar tokens en nodos ni en archivos. Van solo en *Credentials* de n8n.

## 1. Importar
1. n8n → *Workflows* → *Import from file* → `n8n/VisionGuard_v2.2_Hito2_IMPORTAR.json` (conserva tus credenciales Gmail, Sheets, Drive, Telegram y OpenAI gateway).
2. Importar también `n8n/VisionGuard_v2.2_Error_Handler_PUBLICO.json`. En sus nodos `Gmail_Error` y `Telegram_Error`, elegir tus credenciales y escribir tu correo y tu chat ID.
3. En la v2.2: *Settings* → *Error workflow* → `VisionGuard v2.2 - Error Handler`.

## 2. Token de Hugging Face (Transformer NLP)
1. huggingface.co → *Settings* → *Access Tokens* → *New token*, tipo **Read** (gratis).
2. n8n → *Credentials* → *New* → **Header Auth**. *Name* = `Authorization`; *Value* = `Bearer hf_...`.
3. Asignarla al nodo `Embeddings_Transformer_HF`. Sin token, el flujo sigue con las reglas y lo avisa (alerta `NLP_TRANSFORMER_NO_DISPONIBLE`).

## 3. Hoja y tablero
1. Abrir `VisionGuard_Historial_Inspecciones` → *Extensiones* → *Apps Script*.
2. Pegar `dashboard/VisionGuard_Dashboard_Sheets.gs` → guardar → ejecutar **`instalarVisionGuard`** → autorizar.
   - Crea la pestaña `Reportes_NC` (110 reportes simulados) y la pestaña `Dashboard`, con filtros y 9 gráficos.
3. Copiar la URL que aparece en `Dashboard!B2`, del tipo `.../edit#gid=NNN`.
4. En n8n, nodo **Config**, pegarla en `dashboard_url`.
5. **Compartir** la hoja con el profesor como **Lector**. Menú *VisionGuard* → *Verificar permisos* muestra el estado de compartición sin cambiarlo.

## 4. Python en n8n
- `Clasificar_NLP_Python` usa Python nativo.
- Si al ejecutar aparece "Python runner unavailable":
  1. Deshabilitar `Clasificar_NLP_Python`.
  2. Habilitar `Clasificar_NLP_JS_respaldo`.
  3. Conectar la salida de `Parsear_Embeddings` al respaldo y el respaldo a la **entrada 4** del `Merge`.

  El respaldo tiene la misma lógica, ya verificada.

## 5. Primera prueba (sin acciones industriales reales)
1. Subir 1 imagen **con nombre nuevo** a `Inspecciones_Pendientes`, por ejemplo `VG_H2_DEMO_01.jpeg`. La deduplicación omite archivos ya procesados ese día.
2. Abrir el workflow → *Execute workflow*.
3. Esperar a que lleguen el informe por Gmail y Telegram y el correo de aprobación. Responder **Aprobar** o **Rechazar**.
4. Verificar en `Analisis_Integrado` las columnas `estado`, `decision_humana` y `fecha_decision_humana`.
5. Verificar que lleguen el Gmail y el Telegram de la decisión final.
6. Cuando todo funcione: **activar** la v2.2 y **desactivar** la v2.1, para no tener dos flujos que procesen la misma carpeta.

## 6. Notas
- La pestaña `Analisis_Integrado` gana columnas nuevas automáticamente, entre ellas `fuente_analisis`, `alertas`, `nlp_*`, `decision_humana` y `fecha_decision_humana`. Las antiguas no se tocan.
- El historial GRU (`Pronosticos_GRU`) ahora se registra una vez por día y línea.
- Umbrales editables en **Config**: confianza 0,90; pronóstico 7,5 %; discrepancia GRU vs promedio móvil 1,5 pp.
