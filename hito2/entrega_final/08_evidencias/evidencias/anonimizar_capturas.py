"""Copia las capturas del equipo a evidencias/capturas tapando correo e ID de la hoja (cajas negras)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ORIGEN = Path(sys.argv[1])
DEST = Path(__file__).parent / "capturas"
DEST.mkdir(exist_ok=True)
# archivo origen -> (nombre destino, [cajas (x0, y0, x1, y1) a tapar])
CAPTURAS = {
    "1.png": ("01_n8n_ejecucion_108_real_success.png", []),
    "2.png": ("02_n8n_ejecucion_107_real_success.png", []),
    "3.png": ("03_gmail_informe_VG_TEST_021.png", [(128, 228, 470, 256)]),
    "4.png": ("04_sheets_dashboard_filtros_kpis_graficos.png", [(40, 145, 470, 160)]),
    "5.png": ("05_gmail_aprobacion_humana_diagnostico.png", [(80, 0, 1700, 22)]),
    "6.png": ("06_gmail_aprobacion_botones_approve_decline.png", [(860, 540, 1360, 618)]),
    "7.png": ("07_gmail_decision_final_RECHAZAR_VG_TEST_021.png", [(75, 128, 420, 168)]),
    "8.png": ("08_telegram_informes_VG_TEST_021_y_022.png", [(385, 362, 960, 414), (385, 982, 960, 1036)]),
}
for src, (dst, cajas) in CAPTURAS.items():
    im = Image.open(ORIGEN / src).convert("RGB")
    d = ImageDraw.Draw(im)
    for c in cajas:
        d.rectangle(c, fill=(20, 20, 20))
    im.save(DEST / dst)
    print("OK", dst)
