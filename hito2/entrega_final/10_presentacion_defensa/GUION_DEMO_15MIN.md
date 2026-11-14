# Guion de exposición y demostración — 15 minutos

**Antes de entrar:**
1. Despertar las APIs abriendo `/health` de ambas, unos 3 minutos antes.
2. Subir `VG_H2_DEMO_01.jpeg` (defectuosa) a Pendientes **sin ejecutar** el flujo.
3. Abrir en pestañas: el editor n8n, Gmail, Telegram Web, la hoja (`Dashboard`) y el informe.
4. Tener un video de respaldo de una ejecución completa.

| Min | Bloque | Quién | Qué decir / mostrar |
|---|---|---|---|
| 0:00–1:30 | Problema | Integrante 1 | Inspector de fundición, decisión por pieza y por turno. Indicadores: tasa de defectos y escapes. Línea base L1/L2/L3 y falsos negativos 2,87 %. |
| 1:30–3:00 | Datos | Integrante 1 | 3 fuentes: Kaggle (real), serie y NC **simulados** con supuestos explícitos. Reglas de validación y anti-fuga. |
| 3:00–4:30 | Arquitectura | Integrante 2 | Recorrer el canvas: Config → 4 ramas → Merge → Integración → LLM → Validación → Loop humano. Tres zonas: modelos, LLM y control, humano. |
| 4:30–7:30 | **Demo en vivo** | Integrante 2 | *Execute workflow*. Mientras corre (≈ 2-3 min por la espera de Render), explicar el health check y los reintentos. Mostrar en vivo el Gmail con alerta 🚨 y el botón al panel, el Telegram y el correo APROBAR/RECHAZAR. **Rechazar** → mostrar la fila en Sheets con `ACCION_RECHAZADA_POR_HUMANO` y el aviso final. |
| 7:30–10:00 | Modelos y Navaja de Occam | Integrante 3 | ResNet18 vs umbral (97,8 vs 69,5 %) y vs EfficientNet/MobileNet (cifras de Colab). **GRU pierde en prueba contra SES y promedio móvil**: se dice y se explica por qué se mantiene la alerta de discrepancia. NLP: **las reglas (F1 0,515) también le ganan al Transformer (0,347)**; explicar por qué y que el flujo elige en cada corrida el método con mejor F1. |
| 10:00–11:30 | LLM y alucinaciones | Integrante 3 | Recibe el resumen, no los datos crudos. 30 reglas, control numérico y respaldo determinista. Mostrar la prueba 6 (cifras inventadas detectadas). |
| 11:30–13:00 | Tablero y negocio | Integrante 4 | Cambiar un filtro en vivo. ROI 5,5 / 36,5 / 260 %, equilibrio 4,1 h/mes y supuestos que hay que validar. |
| 13:00–15:00 | Riesgos y cierre | Integrante 4 | Falsos negativos ⇒ nunca hay aprobación automática; datos simulados; clave GCP revocada. Próximos pasos: fotos de la planta, Holt-Winters, calibración. |

**Si algo falla en vivo:** decir qué nodo falló y mostrar el correo del Error Handler o la ruta de error (también es evidencia de robustez). Luego pasar al video.

## Preguntas individuales probables (todos deben poder responder)
1. ¿Por qué ResNet18 y no un modelo más grande? (residuales, CPU en Render, 44,7 MB, comparación de Colab)
2. ¿Qué pasa si GPT devuelve un JSON roto? (respaldo determinista, `RESPALDO_DETERMINISTA`, prioridad alta)
3. ¿Cómo evitan que el LLM invente cifras? (control numérico contra los datos de entrada)
4. ¿Por qué el GRU, si pierde contra el promedio móvil? (comparación honesta, alerta de discrepancia, Holt-Winters para producción)
5. ¿Qué es un embedding y cómo clasifican con él? (vector de 384 dim, centroide por causa, coseno)
6. ¿Qué hace `Loop_Inspecciones`? (una aprobación humana por pieza, la clave correcta por pieza)
7. ¿Qué significa Aprobar? (autoriza la acción de inspección, **no** libera la pieza)
8. ¿De dónde sale el 36,5 %? (supuesto base: 15,9 h/mes + 4 escapes/mes; hay que validarlo)
9. ¿Cómo evitan duplicados? (clave `INTEGRADO|archivo|fecha`, deduplicación antes de guardar)
10. ¿Qué datos son simulados y cómo se generaron? (semillas, supuestos, cambio de nivel en L2)
