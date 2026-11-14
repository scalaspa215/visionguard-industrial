
# VISIONGUARD INDUSTRIAL - HITO 2
# API Python para pronostico de defectos
# Datos simulados para demostracion academica

from pathlib import Path
from datetime import date, timedelta
from typing import Literal
import json

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from tensorflow.keras.models import load_model

BASE = Path(__file__).resolve().parent

# Cargar configuracion y modelo entrenado
with open(
    BASE / "metricas_series_temporales.json",
    encoding="utf-8"
) as archivo:
    config = json.load(archivo)

modelo = load_model(
    BASE / "visionguard_gru.keras",
    compile=False
)

media = config["media_train"]
desviacion = config["std_train"]
lineas = config["lineas"]

app = FastAPI(
    title="VisionGuard Industrial - Series Temporales",
    version="2.0",
    description="API academica de pronostico GRU"
)


class Solicitud(BaseModel):
    linea: Literal["L1", "L2", "L3"]
    historial_tasas: list[float] = Field(
        min_length=7,
        max_length=7
    )
    fecha_ultimo_dia: date


def pronosticar(linea, historial, fecha, origen):
    tasas = np.asarray(historial, dtype=float)

    if not np.isfinite(tasas).all():
        raise ValueError("Las tasas deben ser finitas")

    if np.any((tasas < 0) | (tasas > 1)):
        raise ValueError("Las tasas deben estar entre 0 y 1")

    x = np.zeros((1, 7, 4), dtype=np.float32)
    x[0, :, 0] = (tasas - media) / desviacion
    x[0, :, lineas.index(linea) + 1] = 1.0

    pred = modelo.predict(x, verbose=0)[0][0]
    pred = float(np.clip(pred * desviacion + media, 0, 1))

    promedio = float(np.mean(tasas))

    return {
        "linea": linea,
        "fecha_pronostico": str(fecha + timedelta(days=1)),
        "pronostico_gru_pct": round(pred * 100, 2),
        "pronostico_promedio_movil_pct": round(
            promedio * 100, 2
        ),
        "modelo_seleccionado_por_validacion":
            config["seleccion_por_validacion"],
        "origen": origen,
        "requiere_validacion_humana": True
    }


@app.get("/")
def inicio():
    return {
        "proyecto": "VisionGuard Industrial",
        "version": "2.0",
        "estado": "API disponible",
        "modelo": "GRU",
        "horizonte": "1 dia"
    }


@app.get("/health")
def verificar():
    return {
        "status": "ok",
        "modelo_cargado": True
    }


@app.get("/pronosticos-demo")
def pronosticos_demo():
    datos = pd.read_csv(
        BASE / "tasa_defectos_diaria_SIMULADA.csv"
    )
    datos["fecha"] = pd.to_datetime(datos["fecha"])

    resultados = []

    for linea in lineas:
        ultimos = (
            datos[datos["linea"] == linea]
            .sort_values("fecha")
            .tail(7)
        )

        resultados.append(
            pronosticar(
                linea,
                ultimos["tasa_defectos"].tolist(),
                ultimos["fecha"].max().date(),
                "SIMULADO_ACADEMICO_NO_REAL"
            )
        )

    return {
        "tipo": "demostracion_simulada",
        "resultados": resultados
    }


@app.post("/pronosticar")
def pronostico_personalizado(solicitud: Solicitud):
    try:
        return pronosticar(
            solicitud.linea,
            solicitud.historial_tasas,
            solicitud.fecha_ultimo_dia,
            "DATOS_RECIBIDOS_NO_VERIFICADOS"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )
