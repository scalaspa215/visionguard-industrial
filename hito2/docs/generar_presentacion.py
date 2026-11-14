"""Genera la presentacion de defensa (15 min) VisionGuard_Hito2_Presentacion.pptx con cifras de los JSON de resultados."""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

AQUI = Path(__file__).parent
PY = AQUI.parent / "python"
series = json.loads((PY / "series" / "resultados_series.json").read_text(encoding="utf-8"))
nlp = json.loads((PY / "nlp" / "resultados_nlp.json").read_text(encoding="utf-8"))
roi = json.loads((PY / "negocio" / "roi_resultados.json").read_text(encoding="utf-8"))
AZUL, CORAL, GRIS, BLANCO = RGBColor(0x17, 0x28, 0x3F), RGBColor(0xD6, 0x60, 0x5D), RGBColor(0x5D, 0x6F, 0x89), RGBColor(255, 255, 255)

p = Presentation()
p.slide_width, p.slide_height = Inches(13.333), Inches(7.5)
VACIO = p.slide_layouts[6]


def lamina(titulo, sub=None):
    s = p.slides.add_slide(VACIO)
    banda = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, p.slide_width, Inches(1.1))
    banda.fill.solid(); banda.fill.fore_color.rgb = AZUL; banda.line.fill.background()
    tf = banda.text_frame; tf.text = titulo
    tf.paragraphs[0].runs[0].font.size = Pt(30); tf.paragraphs[0].runs[0].font.bold = True
    tf.paragraphs[0].runs[0].font.color.rgb = BLANCO
    if sub:
        t = s.shapes.add_textbox(Inches(0.6), Inches(1.2), Inches(12), Inches(0.5)).text_frame
        t.text = sub; t.paragraphs[0].runs[0].font.size = Pt(14); t.paragraphs[0].runs[0].font.color.rgb = GRIS
    return s


def vinetas(s, items, x=0.6, y=1.8, w=12, tam=20):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(5.3)).text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.text = "• " + it; par.font.size = Pt(tam); par.font.color.rgb = AZUL; par.space_after = Pt(10)


def tabla(s, filas, x=0.6, y=1.9, w=12, tam=14):
    t = s.shapes.add_table(len(filas), len(filas[0]), Inches(x), Inches(y), Inches(w), Inches(0.4 * len(filas))).table
    for i, f in enumerate(filas):
        for j, v in enumerate(f):
            c = t.cell(i, j); c.text = str(v)
            for par in c.text_frame.paragraphs:
                par.font.size = Pt(tam); par.font.bold = i == 0


s = lamina("VisionGuard Industrial · Hito 2", "Control de calidad de piezas fundidas con ResNet18 + GRU + Transformer + GPT-4o mini, orquestado en n8n")
vinetas(s, ["Usuario: inspector de calidad del turno (escala a jefe de calidad)",
            "Decisión: por pieza → apartar / revisar / continuar validación; por turno → qué línea revisar",
            "Indicadores: tasa de defectos por línea (%) y escapes al cliente por mes",
            "Prototipo académico: imágenes públicas (Kaggle); serie y reportes NC SIMULADOS",
            "Ninguna pieza se aprueba automáticamente"])

s = lamina("Datos y validación")
tabla(s, [["Fuente", "Tipo", "Origen", "Volumen"],
          ["Imágenes de piezas", "No estructurado", "Kaggle Casting (real)", "7.348 (test 715)"],
          ["Tasa diaria de defectos", "Serie temporal", "Simulado, semilla 20261112", "180 días × 3 líneas"],
          ["Reportes de no conformidad", "Texto", "Simulado, semilla 20261114", "110 (50/40/20)"],
          ["Historial y decisiones", "Estructurado", "Generado por el flujo", "1 fila por pieza/día"]])
vinetas(s, ["8 reglas de validación en el flujo: tamaño/formato de imagen, clases, rangos, duplicados, textos, embeddings",
            "Anti-fuga en NLP: frases de prueba no vistas en referencia"], y=4.3, tam=16)

s = lamina("Arquitectura n8n v2.2 (61 nodos)")
vinetas(s, ["Disparo por turno (07/15/23 h) → Config → 4 ramas: ResNet18 · GRU · NLP almacenado · Transformer en vivo",
            "Merge → Integración (resumen + alertas) → GPT-4o mini (JSON) → Validación de seguridad",
            "Dedupe → Sheets → bucle por pieza: Gmail + Telegram + aprobación humana (8 h) → registro y aviso final",
            "Robustez: health checks, reintentos, rutas de error, respaldo determinista, Error Handler",
            "Python en el flujo: nodo Clasificar_NLP_Python + 2 APIs FastAPI"], tam=18)

s = lamina("Imágenes: ResNet18 vs alternativas", "Test independiente de 715 imágenes")
tabla(s, [["Métrica", "Umbral simple", "ResNet18"], ["Accuracy", "69,51 %", "97,76 %"],
          ["Precisión defectuosa", "78,18 %", "99,32 %"], ["Recall defectuosa", "71,96 %", "97,13 %"],
          ["F1 defectuosa", "74,94 %", "98,21 %"], ["Falsos negativos", "—", "13 / 453"]], w=8)
vinetas(s, ["EfficientNet-B0 y MobileNetV3: notebook Colab listo (misma partición, McNemar)"], y=5.0, tam=16)

m = {(x["conjunto"], x["modelo"]): x for x in series["metricas"]}
orden = sorted({x["modelo"] for x in series["metricas"]}, key=lambda k: m[("test", k)]["MAE_pp"])
s = lamina("Serie temporal: GRU vs clásicos (Navaja de Occam)", "MAE en puntos porcentuales, 1 día adelante, 81 puntos por conjunto, datos simulados")
tabla(s, [["Modelo", "MAE validación", "MAE prueba"]] +
      [[k, f'{m[("val", k)]["MAE_pp"]:.3f}', f'{m[("test", k)]["MAE_pp"]:.3f}'] for k in orden], w=8, tam=13)
vinetas(s, ["El GRU NO gana en prueba → se usa como demostración + alerta de discrepancia ≥ 1,5 pp",
            f'CUSUM detecta el cambio de nivel de L2 con {series["cusum"]["retardo_dias"]} días de retardo'], y=5.4, tam=15)

s = lamina("Texto: Transformer MiniLM vs reglas", "40 reportes NC simulados de prueba")
tabla(s, [["Método", "Accuracy", "F1 macro"],
          ["Reglas fijas", f'{nlp["reglas"]["accuracy"]:.3f}', f'{nlp["reglas"]["f1_macro"]:.3f}'],
          ["Transformer MiniLM", f'{nlp["transformer"]["accuracy"]:.3f}', f'{nlp["transformer"]["f1_macro"]:.3f}'],
          ["Híbrido (post hoc)", f'{nlp["hibrido_post_hoc"]["accuracy"]:.3f}', f'{nlp["hibrido_post_hoc"]["f1_macro"]:.3f}']], w=8)
vinetas(s, ["Las reglas ganan: el flujo usa en cada corrida el método con mejor F1 medido",
            "Causa probable: contexto común domina los embeddings; pocas referencias por causa"], y=4.0, tam=16)

s = lamina("LLM y control de alucinaciones")
vinetas(s, ["El LLM recibe el resumen de los modelos, nunca la tabla cruda; 30 reglas + JSON de 11 claves",
            "Validación: estructura, reglas de seguridad corregidas (LLM_CORREGIDO), prioridad alta si hay defecto",
            "Cada cifra del texto se contrasta con los datos → cifras no respaldadas marcadas",
            "JSON inválido o LLM caído → análisis determinista de respaldo; el flujo no se cae",
            "15/15 pruebas unitarias de estos casos"], tam=18)

e = roi["escenarios"]
s = lamina("Negocio: ROI (estimación académica)")
tabla(s, [["Escenario", "Horas/mes", "Escapes/mes", "ROI año 1", "Recuperación"]] +
      [[k, v["horas_ahorradas_mes"], v["escapes_evitados_mes"], f'{v["roi_anio1_pct"]} %', f'{v["recuperacion_meses"]} meses'] for k, v in e.items()], w=10)
vinetas(s, [f'Equilibrio: {roi["equilibrio_horas_mes_con_4_escapes"]} h/mes ahorradas',
            "Base 36,5 % requiere ≈15,9 h/mes + 4 escapes evitados: validar midiendo el registro manual"], y=4.0, tam=16)

s = lamina("Riesgos, ética y control humano")
vinetas(s, ["Falso negativo (2,87 %) → revisión humana obligatoria para toda pieza",
            "Aprobar autoriza la acción de inspección, NO libera la pieza",
            "Sin respuesta en 8 h → SIN_RESPUESTA_HUMANA_ESCALAR",
            "Datos simulados marcados en todo el flujo; export público sin credenciales",
            "Clave de servicio de Google Cloud anterior: revocada / a revocar"], tam=18)

s = lamina("Cierre y próximos pasos")
vinetas(s, ["Sistema integrado: 3 modelos + LLM + humano + tablero, con comparación honesta frente a alternativas simples",
            "Próximos pasos: fotos reales de planta, Holt-Winters en producción, calibración de ResNet18, reportes NC reales",
            "Repositorio: github.com/scalaspa215/visionguard-industrial (carpeta hito2)"], tam=18)

out = AQUI / "VisionGuard_Hito2_Presentacion.pptx"
p.save(out)
print("OK", out.name, len(p.slides), "láminas")
