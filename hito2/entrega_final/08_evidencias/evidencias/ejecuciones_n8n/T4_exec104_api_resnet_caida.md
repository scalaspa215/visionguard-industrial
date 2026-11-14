# T4 · Ejecución 104 · API ResNet18 no disponible (fallo controlado, pin data)

- Ejecución n8n: **104** · modo `manual` (`test_workflow`) · 2026-11-14T21:24:24Z → 21:26:56Z · estado final **success**
- Entrada simulada: ambos `/health` responden `503 Render - Application loading` (el error real observado en la ejecución 99). Gmail y Telegram están simulados: **no se envió nada real**.

| Nodo | Resultado observado |
|---|---|
| `HTTP Request1` (`/health`) | error 503 (simulado); `onError: continueRegularOutput`, así que no se cae |
| `If1` | salida **falsa** |
| `Wait` | espera real de **60 000 ms** (arranque en frío de Render) |
| `HTTP Request2` (`/health`, segundo intento) | error 503 (simulado) |
| `If2` | salida **falsa** |
| `Send a message1` (Gmail "ERROR CRÍTICO - API NO DISPONIBLE", con enlace al panel) | ejecutado |
| `Telegram_API_Caida` | ejecutado |
| `Search files and folders` y la rama de imágenes | no se ejecutan; no se procesan inspecciones sin modelo |

**Conclusión:** cuando la API de visión no responde, el flujo reintenta tras 60 s, avisa por Gmail y Telegram y no genera registros ni aprobaciones con datos incompletos.

**Error Handler:** el workflow `VisionGuard v2.2 - Error Handler` está publicado y configurado como *Error workflow*. n8n solo lo dispara en ejecuciones de producción (programadas), no en las de prueba. Por eso su disparo real (B9) queda pendiente de una ejecución programada o autorizada.
