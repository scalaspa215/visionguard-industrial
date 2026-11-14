# T5 · Ejecución 105 · Archivo inválido + inspección duplicada (B5 + B7, pin data)

- Ejecución n8n: **105** · modo `manual` (`test_workflow`) · 2026-11-14T21:26:40Z → 21:28:13Z · estado **success**
- Entradas simuladas:
  - `VG_PIN_T5_CORRUPTO.jpeg`: la API devuelve `400 Archivo de imagen no valido`. `HTTP Request` tiene `onError: continueRegularOutput`.
  - `VG_PIN_T1_DEF.jpeg`: **la misma imagen ya procesada en la ejecución 101 el mismo día**.
- Gmail, Telegram, Sheets y Drive están simulados.

| Nodo | Resultado observado |
|---|---|
| `HTTP Request` (ResNet18) | 2 ítems: uno con `error` y uno válido. El flujo **no se cae** |
| `Integracion_3_Modelos` | analiza solo la imagen válida y agrega la alerta `ERROR_INFERENCIA_IMAGEN: 1 imagen(es) sin resultado valido de la API` |
| `Validacion_Seguridad_Final` | `LLM_VALIDADO`, prioridad alta |
| `Preparar_Registro_Integrado` | clave `INTEGRADO\|VG_PIN_T1_DEF.jpeg\|2026-11-14`, la misma que en la ejecución 101 |
| `Evitar_Notificaciones_Duplicadas` | salida "mantener" vacía; el ítem sale por la salida de **descartados** (clave ya vista en una ejecución anterior) |
| `Guardar_Analisis_Integrado` y nodos siguientes (avisos, aprobación) | **no se ejecutan**: no hay segunda fila, segundo correo ni segunda aprobación, y la decisión humana registrada en la ejecución 101 no se sobrescribe |

**Conclusión:** un archivo corrupto se aísla y se informa como alerta. Una imagen repetida el mismo día no se vuelve a registrar ni a notificar.

**Limitación conocida:** si **todas** las imágenes de un turno son duplicadas, ese turno no envía ningún correo. Es intencional, para evitar spam, y queda documentado.
