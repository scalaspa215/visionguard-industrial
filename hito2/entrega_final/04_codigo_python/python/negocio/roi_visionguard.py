"""
VisionGuard Industrial - Hito 2
Evaluacion economica ACADEMICA: costos, beneficios, ROI y recuperacion.

IMPORTANTE: todas las cifras son SUPUESTOS documentados, no mediciones de una
planta. El ROI de 36,5 % reportado antes por el equipo se conserva como
escenario BASE; como sus supuestos no estaban documentados, aqui se calcula que
beneficio lo reproduce con los costos explicitos de abajo (variable libre:
horas de inspector ahorradas por mes) para poder discutir si es plausible.

ROI anio 1 = (Beneficio anual - Costo anual total) / Costo anual total
Costo anual total = costo operativo anual + implementacion (unica vez)
Recuperacion (meses) = implementacion / ((beneficio anual - costo operativo) / 12)
"""
import csv
import json
from pathlib import Path

AQUI = Path(__file__).parent
USD_CLP = 950          # tipo de cambio supuesto
HORA_INSPECTOR = 8500  # CLP/h, costo empresa de un inspector de calidad (supuesto)
HORA_INGENIERO = 25000 # CLP/h, mantencion del sistema (supuesto)

COSTOS_OPERACION = {   # CLP por anio
    "n8n Cloud (plan Starter, ~24 EUR/mes)": 27000 * 12,
    "OpenAI GPT-4o mini (3 ejecuciones/dia, ~3k tokens c/u)": round(1 * USD_CLP * 12),
    "Render: 2 APIs Python (plan Starter 7 USD/mes c/u)": 2 * 7 * USD_CLP * 12,
    "Hugging Face (plan PRO 9 USD/mes, embeddings)": 9 * USD_CLP * 12,
    "Mantencion (4 h/mes de ingeniero)": 4 * HORA_INGENIERO * 12,
}
IMPLEMENTACION = 60 * HORA_INGENIERO  # 60 h de puesta en marcha (unica vez)
COSTO_ESCAPE = 60000                  # CLP por pieza defectuosa que llega al cliente (reproceso+flete+reclamo)

ESCENARIOS = {
    #              horas ahorradas/mes, escapes evitados/mes
    "Conservador": {"horas_mes": 20, "escapes_mes": 2},
    "Base":        {"horas_mes": None, "escapes_mes": 4, "roi_objetivo": 0.365},
    "Optimista":   {"horas_mes": 60, "escapes_mes": 8},
}


def calcular(horas_mes, escapes_mes):
    c_op = sum(COSTOS_OPERACION.values())
    beneficio = horas_mes * 12 * HORA_INSPECTOR + escapes_mes * 12 * COSTO_ESCAPE
    total = c_op + IMPLEMENTACION
    neto_mensual = (beneficio - c_op) / 12
    return {
        "horas_ahorradas_mes": round(horas_mes, 1),
        "escapes_evitados_mes": escapes_mes,
        "beneficio_anual_clp": round(beneficio),
        "costo_operacion_anual_clp": round(c_op),
        "implementacion_clp": IMPLEMENTACION,
        "costo_total_anio1_clp": round(total),
        "roi_anio1_pct": round(100 * (beneficio - total) / total, 1),
        "roi_anio2_pct": round(100 * (beneficio - c_op) / c_op, 1),
        "recuperacion_meses": round(IMPLEMENTACION / neto_mensual, 1) if neto_mensual > 0 else None,
    }


def main():
    c_op = sum(COSTOS_OPERACION.values())
    total = c_op + IMPLEMENTACION
    filas = {}
    for nombre, e in ESCENARIOS.items():
        horas = e["horas_mes"]
        if horas is None:  # despejar horas para reproducir el ROI objetivo del equipo
            beneficio_obj = (1 + e["roi_objetivo"]) * total
            horas = (beneficio_obj - e["escapes_mes"] * 12 * COSTO_ESCAPE) / (12 * HORA_INSPECTOR)
        filas[nombre] = calcular(horas, e["escapes_mes"])

    # Sensibilidad: ROI anio 1 segun horas ahorradas (escapes del escenario base)
    sens = [{"horas_mes": h, "roi_anio1_pct": calcular(h, 4)["roi_anio1_pct"]} for h in range(0, 65, 5)]
    # Punto de equilibrio en horas (ROI anio 1 = 0) con 4 escapes/mes
    h_eq = (total - 4 * 12 * COSTO_ESCAPE) / (12 * HORA_INSPECTOR)

    salida = {"naturaleza": "ESTIMACION_ACADEMICA_NO_RESULTADO_INDUSTRIAL",
              "supuestos": {"usd_clp": USD_CLP, "hora_inspector_clp": HORA_INSPECTOR,
                            "hora_ingeniero_clp": HORA_INGENIERO, "costo_escape_clp": COSTO_ESCAPE,
                            "costos_operacion_clp_anio": COSTOS_OPERACION, "implementacion_clp": IMPLEMENTACION},
              "escenarios": filas, "sensibilidad_horas": sens,
              "equilibrio_horas_mes_con_4_escapes": round(h_eq, 1)}
    (AQUI / "roi_resultados.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    with (AQUI / "roi_escenarios.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["escenario", *next(iter(filas.values())).keys()])
        w.writeheader()
        for k, v in filas.items():
            w.writerow({"escenario": k, **v})
    print(json.dumps(salida["escenarios"], indent=1, ensure_ascii=False))
    print("Equilibrio:", round(h_eq, 1), "h/mes")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
        nombres = list(filas)
        ax[0].bar(nombres, [filas[n]["roi_anio1_pct"] for n in nombres], color=["#d9864c", "#3557bd", "#258c7a"])
        for i, n in enumerate(nombres):
            ax[0].text(i, filas[n]["roi_anio1_pct"], f'{filas[n]["roi_anio1_pct"]} %', ha="center", va="bottom")
        ax[0].set_title("ROI año 1 por escenario (estimación académica)")
        ax[0].axhline(0, color="#888", lw=0.8)
        ax[1].plot([s["horas_mes"] for s in sens], [s["roi_anio1_pct"] for s in sens], marker="o", color="#3557bd")
        ax[1].axhline(0, color="#888", lw=0.8)
        ax[1].axvline(h_eq, color="#d6605d", ls="--", lw=1)
        ax[1].set_xlabel("Horas de inspector ahorradas por mes")
        ax[1].set_ylabel("ROI año 1 (%)")
        ax[1].set_title(f"Sensibilidad (equilibrio ≈ {h_eq:.1f} h/mes)")
        fig.tight_layout()
        fig.savefig(AQUI / "roi_escenarios.png", dpi=140)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
