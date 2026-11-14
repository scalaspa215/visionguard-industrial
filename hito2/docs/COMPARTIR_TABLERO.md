# Compartir el tablero con el profesor y la ayudante (1 clic)

El flujo auxiliar **`VisionGuard - Compartir tablero (una vez)`** ya está creado en n8n. Comparte la hoja `VisionGuard_Historial_Inspecciones` como **Lector** con:

- Profesor: Danilo Gómez
- Ayudante: María Jesús Salinas

Usa los correos institucionales de la tabla del programa del curso. **No envía** correo de aviso (`sendNotificationEmail: false`): el enlace va en el informe y en la presentación.

**Cómo ejecutarlo:**
1. Abre n8n → *Overview*.
2. Abre **VisionGuard - Compartir tablero (una vez)**.
3. Pulsa **Execute workflow**. Los dos nodos deben quedar en verde.
4. Opcional: después, archiva ese flujo, porque ya no se necesita.

**Alternativa manual:** en Google Sheets, botón **Compartir** → agrega los dos correos → rol **Lector** → desmarca "Notificar" → **Enviar**.

> Claude no lo ejecutó porque el control de permisos de la sesión bloqueó compartir documentos con terceros. La acción queda en tus manos.
