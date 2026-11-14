"""
VisionGuard Industrial - Hito 2
Comparacion de pronosticos de la tasa diaria de defectos (1 dia adelante).

Modelos (todos evaluados con la MISMA particion cronologica del notebook GRU,
mismo horizonte y mismas metricas en puntos porcentuales):
  1. Ingenuo            : y_hat(t) = y(t-1)
  2. Promedio movil 7d  : media de los 7 dias previos (base del notebook)
  3. SES                : suavizamiento exponencial simple (alpha ajustado en train)
  4. Holt               : nivel + tendencia (alpha, beta ajustados en train)
  5. Holt-Winters 7d    : nivel + estacionalidad semanal aditiva (ajustado en train)
  6. Regresion          : MCO con media de 7 lags + dia de semana (ajustada en train)
  7. GRU                : modelo Keras desplegado; se consulta su API real
                          POST /pronosticar con los 7 dias previos de cada punto.

Ademas: deteccion de cambio de nivel (CUSUM) para la linea L2, cuyo cambio
simulado (+1,8 pp desde el dia 120) es conocido -> se mide el retardo.

Datos: tasa_defectos_diaria_SIMULADA.csv (540 filas, 3 lineas x 180 dias),
       SIMULADOS con fines academicos (ver notebook, semilla 20261112).
Uso:   python comparar_series.py [--sin-api]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

AQUI = Path(__file__).parent
API_GRU = "https://visionguard-series-api.onrender.com/pronosticar"


# ---------- 1. Datos y particion identica al notebook ----------
def cargar():
    df = pd.read_csv(AQUI / "tasa_defectos_diaria_SIMULADA.csv", parse_dates=["fecha"])
    # Validacion minima (tipos, nulos, duplicados, rangos)
    assert df.isnull().sum().sum() == 0, "Hay nulos"
    assert not df.duplicated(["fecha", "linea"]).any(), "Hay duplicados"
    assert df["tasa_defectos"].between(0, 1).all(), "Tasa fuera de [0,1]"
    assert (df["piezas_defectuosas"] <= df["piezas_inspeccionadas"]).all()
    fechas = sorted(df["fecha"].unique())
    n = len(fechas)
    c_tr, c_va = round(n * 0.70), round(n * 0.85)
    return df, set(fechas[:c_tr]), set(fechas[c_tr:c_va]), set(fechas[c_va:])


# ---------- 2. Modelos clasicos (recursiones explicitas) ----------
def pred_ses(y, a):
    l, out = y[0], [np.nan]
    for t in range(1, len(y)):
        out.append(l)                      # pronostico de y[t] con info hasta t-1
        l = a * y[t] + (1 - a) * l
    return np.array(out)


def pred_holt(y, a, b):
    l, tr, out = y[0], y[1] - y[0], [np.nan]
    for t in range(1, len(y)):
        out.append(l + tr)
        l_new = a * y[t] + (1 - a) * (l + tr)
        tr = b * (l_new - l) + (1 - b) * tr
        l = l_new
    return np.array(out)


def pred_hw(y, a, g, m=7):
    l = y[:m].mean()
    s = list(y[:m] - l)
    out = [np.nan] * m
    for t in range(m, len(y)):
        out.append(l + s[t - m])
        l_new = a * (y[t] - s[t - m]) + (1 - a) * l
        s.append(g * (y[t] - l_new) + (1 - g) * s[t - m])
        l = l_new
    return np.array(out)


def ajustar(fn, y_train, x0, n_params):
    """Minimiza el error cuadratico 1 paso adelante SOLO en entrenamiento."""
    def sse(p):
        e = y_train - fn(y_train, *p)
        return np.nansum(e ** 2)
    res = minimize(sse, x0, bounds=[(0.01, 0.99)] * n_params, method="L-BFGS-B")
    return res.x


def metricas(real, pred):
    e = (real - pred) * 100
    return {"MAE_pp": round(float(np.mean(np.abs(e))), 4),
            "RMSE_pp": round(float(np.sqrt(np.mean(e ** 2))), 4),
            "n": int(len(e))}


# ---------- 3. GRU via API desplegada ----------
def gru_api(linea, historial, fecha_ultimo, reintentos=4):
    cuerpo = json.dumps({"linea": linea, "historial_tasas": [float(v) for v in historial],
                         "fecha_ultimo_dia": str(pd.Timestamp(fecha_ultimo).date())}).encode()
    for intento in range(reintentos):
        try:
            req = urllib.request.Request(API_GRU, data=cuerpo, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())["pronostico_gru_pct"] / 100
        except Exception:
            time.sleep(5 * (intento + 1))
    raise RuntimeError("API GRU no respondio")


def cusum(y, objetivo, k, h):
    """CUSUM superior: alarma cuando la suma acumulada supera h."""
    s = 0.0
    for t, v in enumerate(y):
        s = max(0.0, s + (v - objetivo - k))
        if s > h:
            return t
    return None


def main():
    usar_api = "--sin-api" not in sys.argv
    df, d_tr, d_va, d_te = cargar()
    filas = []
    for linea in sorted(df["linea"].unique()):
        s = df[df["linea"] == linea].sort_values("fecha").reset_index(drop=True)
        y = s["tasa_defectos"].to_numpy()
        es_tr = s["fecha"].isin(d_tr).to_numpy()
        y_tr = y[es_tr]

        p = {"Ingenuo": np.r_[np.nan, y[:-1]],
             "Promedio movil 7d": pd.Series(y).shift(1).rolling(7, min_periods=7).mean().to_numpy()}
        a = ajustar(pred_ses, y_tr, [0.3], 1)
        p["SES"] = pred_ses(y, *a)
        ab = ajustar(pred_holt, y_tr, [0.3, 0.1], 2)
        p["Holt"] = pred_holt(y, *ab)
        ag = ajustar(pred_hw, y_tr, [0.3, 0.1], 2)
        p["Holt-Winters 7d"] = pred_hw(y, *ag)

        # Regresion: media de 7 lags + dummies de dia de semana, MCO en train
        lag7 = pd.Series(y).shift(1).rolling(7, min_periods=7).mean().to_numpy()
        dow = pd.get_dummies(s["fecha"].dt.dayofweek, drop_first=True).to_numpy(float)
        X = np.column_stack([np.ones(len(y)), lag7, dow])
        ok = es_tr & ~np.isnan(lag7)
        beta, *_ = np.linalg.lstsq(X[ok], y[ok], rcond=None)
        p["Regresion lag+semana"] = X @ beta

        for i in range(len(s)):
            conj = ("train" if s.loc[i, "fecha"] in d_tr else
                    "val" if s.loc[i, "fecha"] in d_va else "test")
            fila = {"linea": linea, "fecha": s.loc[i, "fecha"], "conjunto": conj, "real": y[i]}
            fila.update({k: v[i] for k, v in p.items()})
            if usar_api and conj in ("val", "test") and i >= 7:
                fila["GRU"] = gru_api(linea, y[i - 7:i], s.loc[i - 1, "fecha"])
            filas.append(fila)

        print(f"{linea}: SES a={a.round(3)}, Holt a,b={ab.round(3)}, HW a,g={ag.round(3)}")

    res = pd.DataFrame(filas)
    res.to_csv(AQUI / "predicciones_series.csv", index=False)
    modelos = [c for c in res.columns if c not in ("linea", "fecha", "conjunto", "real")]
    tabla = []
    for conj in ("val", "test"):
        d = res[res["conjunto"] == conj]
        for m in modelos:
            dd = d.dropna(subset=[m])
            tabla.append({"conjunto": conj, "modelo": m, **metricas(dd["real"].to_numpy(), dd[m].to_numpy())})
    tabla = pd.DataFrame(tabla)
    print(tabla.pivot(index="modelo", columns="conjunto", values="MAE_pp").sort_values("test"))

    # CUSUM sobre L2 (cambio simulado conocido en el dia 120)
    l2 = df[df["linea"] == "L2"].sort_values("fecha")["tasa_defectos"].to_numpy()
    base_tr = l2[:126]
    obj, sd = base_tr[:100].mean(), base_tr[:100].std()
    alarma = cusum(l2[100:], obj, k=0.5 * sd, h=5 * sd)
    deteccion = {"linea": "L2", "cambio_real_dia": 120,
                 "alarma_dia": None if alarma is None else 100 + alarma,
                 "retardo_dias": None if alarma is None else 100 + alarma - 120,
                 "parametros": "k=0.5 sigma, h=5 sigma; referencia dias 0-99"}
    print("CUSUM:", deteccion)

    salida = {"datos": "SIMULADOS_ACADEMICOS", "horizonte_dias": 1,
              "metricas": tabla.to_dict(orient="records"), "cusum": deteccion}
    (AQUI / "resultados_series.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False,
                                                            default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
