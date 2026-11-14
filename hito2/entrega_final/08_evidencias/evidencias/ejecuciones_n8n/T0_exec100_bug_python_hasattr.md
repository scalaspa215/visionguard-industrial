# T0 · Ejecución 100 · Bug real detectado en n8n (antes de la corrección)

- Workflow: `VisionGuard v2.2 - Hito 2 FINAL` (id `VovpPUZ4J1sAIOVT`), ejecución **100**, modo `manual` (test con pin data), estado **error**.
- Fecha: 2026-11-14T21:16:53Z → 21:18:26Z.
- Nodo que falló: `Clasificar_NLP_Python` (Code, `language: pythonNative`).
- Mensaje: `name 'hasattr' is not defined` (`WrappedExecutionError` en `PythonTaskRunnerSandbox`).

**Causa:** el runner Python nativo de n8n Cloud restringe los *builtins*: `hasattr` no existe en su sandbox. El código intentaba ser compatible con el runtime antiguo (Pyodide) usando `hasattr`/`isinstance`.

**Efecto:** el Merge de 4 entradas quedaba esperando la entrada NLP y el flujo se detenía antes del LLM. Ninguna inspección habría llegado a Gmail o Telegram.

**Corrección (versión `60e36d82…`, 2026-11-14T21:19Z, vía MCP):** la entrada se lee con `_items[0]["json"]`, sin `hasattr` ni `isinstance`. Mismo cambio en `python/n8n_nodes/clasificar_nlp.py`.

**Verificación:** la ejecución 101 (T1), con los mismos datos de entrada, terminó con estado `success` y el nodo produjo la salida esperada (ver `T1_exec101_*.md`).
