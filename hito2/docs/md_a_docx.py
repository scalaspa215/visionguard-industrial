"""Convierte INFORME_TECNICO_HITO2.md a .docx (encabezados, tablas, listas, codigo)."""
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor

AQUI = Path(__file__).parent
lineas = (AQUI / "INFORME_TECNICO_HITO2.md").read_text(encoding="utf-8").splitlines()
doc = Document()
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(10)


def texto_rico(par, s):
    for parte in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)", s):
        if not parte:
            continue
        if parte.startswith("**"):
            par.add_run(parte[2:-2]).bold = True
        elif parte.startswith("`"):
            r = par.add_run(parte[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(9)
        elif parte.startswith("*") and len(parte) > 2:
            par.add_run(parte[1:-1]).italic = True
        else:
            par.add_run(parte)


i = 0
while i < len(lineas):
    l = lineas[i]
    if l.startswith("```"):
        bloque = []
        i += 1
        while i < len(lineas) and not lineas[i].startswith("```"):
            bloque.append(lineas[i]); i += 1
        p = doc.add_paragraph()
        r = p.add_run("\n".join(bloque)); r.font.name = "Consolas"; r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(0x17, 0x28, 0x3F)
    elif l.startswith("|"):
        filas = []
        while i < len(lineas) and lineas[i].startswith("|"):
            if not re.match(r"^\|[\s\-|:]+\|$", lineas[i]):
                filas.append([c.strip() for c in lineas[i].strip("|").split("|")])
            i += 1
        t = doc.add_table(rows=len(filas), cols=len(filas[0]))
        t.style = "Light Grid Accent 1"
        for f, fila in enumerate(filas):
            for c, val in enumerate(fila[:len(filas[0])]):
                celda = t.cell(f, c); celda.text = ""
                texto_rico(celda.paragraphs[0], val)
                for r in celda.paragraphs[0].runs:
                    r.font.size = Pt(8.5)
                    if f == 0:
                        r.bold = True
        continue
    elif l.startswith("#"):
        nivel = len(l) - len(l.lstrip("#"))
        doc.add_heading(l.lstrip("# ").strip(), level=min(nivel, 3))
    elif re.match(r"^\s*(- |\d+\. )", l):
        estilo = "List Number" if re.match(r"^\s*\d+\. ", l) else "List Bullet"
        texto_rico(doc.add_paragraph(style=estilo), re.sub(r"^\s*(- |\d+\. )", "", l))
    elif l.strip() == "---":
        pass
    elif l.strip():
        texto_rico(doc.add_paragraph(), l)
    i += 1

doc.save(AQUI / "INFORME_TECNICO_HITO2.docx")
print("OK INFORME_TECNICO_HITO2.docx")
