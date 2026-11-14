"""
VisionGuard Industrial - Hito 2
Generador reproducible de REPORTES DE NO CONFORMIDAD (NC) SIMULADOS.

Por que simulados: no se encontro un conjunto publico de reportes NC de
fundicion en espanol con su causa etiquetada. Supuestos explicitos:
  * 5 causas (ver nlp_comun.CLASES), balanceadas.
  * Cada reporte = contexto (linea, pieza, turno, deteccion) + descripcion de causa.
  * ~50 % de las descripciones usa vocabulario tecnico directo (palabras que
    tambien estan en las reglas) y ~50 % usa parafrasis coloquiales SIN esas
    palabras (p. ej. "burbujas internas" en vez de "porosidad"), como escribe
    un operador real. Esto evita que el conjunto favorezca artificialmente a
    las reglas o al Transformer.
  * Algunos reportes mencionan terminos de otra clase como distractor
    (p. ej. "el operador detecto porosidad").
Particion: referencia (ejemplos etiquetados que usa el clasificador por
embeddings), prueba (evaluacion; NO se usa para ajustar nada) y operacion
(reportes nuevos sin etiqueta visible, que el flujo clasifica cada turno).

Uso:  python generar_reportes_nc.py  -> reportes_nc_simulados.csv (+ _clave.csv)
"""
import csv
import random
from pathlib import Path

SEMILLA = 20261114
rng = random.Random(SEMILLA)

CAUSAS = {
    "materia_prima": {
        "directo": [
            "se observa porosidad en la zona de la brida",
            "presenta inclusiones no metalicas en la superficie mecanizada",
            "la aleacion del lote de material no cumple la composicion especificada",
            "impurezas visibles despues del granallado",
            "poros abiertos tras el mecanizado del asiento",
            "colada con exceso de escoria atrapada en la pieza",
        ],
        "parafrasis": [
            "aparecen pequenas burbujas internas al cortar la pieza",
            "hay puntos negros incrustados que no salen al limpiar",
            "el certificado del proveedor no coincide con el analisis del laboratorio",
            "se ven huecos diminutos al pulir la cara del rodete",
            "el metal recibido esta oxidado y contaminado",
            "el espectrometro muestra cobre por sobre lo permitido en la carga",
        ],
    },
    "ajuste_proceso": {
        "directo": [
            "la temperatura de vertido estuvo bajo el minimo del procedimiento",
            "presion de inyeccion inestable durante el ciclo",
            "parametro de enfriamiento modificado sin autorizacion",
            "tiempo de ciclo reducido para recuperar produccion",
            "velocidad de llenado del molde excesiva",
        ],
        "parafrasis": [
            "el horno no alcanzo el punto de trabajo antes de vaciar",
            "la maquina quedo con la receta del producto anterior",
            "se apuro el desmoldeo y la pieza salio aun blanda",
            "el termopar marcaba bien pero el metal llego frio",
            "se cambio la configuracion del equipo en el cambio de formato",
            "la camara de aire no se purgo y el llenado fue irregular",
        ],
    },
    "herramienta_molde": {
        "directo": [
            "el molde presenta desgaste en la linea de particion",
            "matriz con fisura en la cavidad dos",
            "herramienta de corte desgastada deja rebaba",
            "cavidad danada genera marca repetitiva en todas las piezas",
            "desgaste del noyo provoca diametro fuera de tolerancia",
        ],
        "parafrasis": [
            "la misma marca aparece en la misma posicion pieza tras pieza",
            "el inserto ya cumplio su vida util y no fue reemplazado",
            "se nota un escalon en la junta donde cierran las dos mitades",
            "el utillaje tiene un despostillado que se copia en la pieza",
            "la broca se esta comiendo y el agujero sale ovalado",
            "el modelo de arena quedo con una esquina rota",
        ],
    },
    "operacion_manual": {
        "directo": [
            "el operador no siguio el procedimiento de desbarbado",
            "golpe durante la manipulacion en el traslado a bodega",
            "caida de la pieza desde el carro de transporte",
            "manipulacion sin proteccion dejo rayas en la cara sellante",
            "el turno de noche omitio la limpieza del area",
        ],
        "parafrasis": [
            "la pieza se resbalo de las manos al sacarla de la jaula",
            "quedaron mal apiladas y se rozaron entre ellas",
            "se uso la grua sin eslinga blanda y se marco el borde",
            "el personal nuevo no recibio la instruccion de trabajo",
            "alguien dejo la pieza en el piso junto al paso de la grua horquilla",
            "se salto el paso de revision porque faltaba gente",
        ],
    },
    "medicion_inspeccion": {
        "directo": [
            "el instrumento de control estaba fuera de calibracion",
            "error de medicion con el pie de metro en el diametro interior",
            "el micrometro de la estacion dos no tiene calibracion vigente",
            "la galga pasa no pasa estaba danada",
            "medicion registrada en la unidad equivocada",
        ],
        "parafrasis": [
            "al repetir el control en laboratorio la pieza si cumple",
            "dos inspectores obtienen valores distintos en la misma cota",
            "el patron de referencia se cayo y nadie lo verifico despues",
            "el registro del equipo de control tiene la fecha vencida",
            "se rechazo la pieza pero la maquina tridimensional la acepta",
            "la lectura cambia segun como se apoya el comparador",
        ],
    },
}

LINEAS = ["L1", "L2", "L3"]
PIEZAS = ["rodete", "carcasa de bomba", "brida", "tapa de valvula", "soporte"]
DETECCION = ["en inspeccion final", "en control de recepcion del cliente", "en el mecanizado",
             "en la prueba de estanqueidad", "durante la inspeccion visual"]
DISTRACTORES = ["El operador de turno lo informo.", "Se aparto el lote.",
                "Se detecto en el turno de tarde.", "Se requiere revisar el procedimiento."]


def armar_reporte(causa: str, i: int, rol: str) -> str:
    banco = CAUSAS[causa]["directo"] if i % 2 == 0 else CAUSAS[causa]["parafrasis"]
    # Anti-fuga: 'referencia' usa solo las 3 primeras frases de cada banco y
    # 'prueba'/'operacion' solo las restantes. Asi ningun reporte de prueba
    # repite literalmente una descripcion vista por el clasificador.
    banco = banco[:3] if rol == "referencia" else banco[3:]
    desc = rng.choice(banco)
    texto = (f"Linea {rng.choice(LINEAS)}, {rng.choice(PIEZAS)}: "
             f"no conformidad detectada {rng.choice(DETECCION)}; {desc}.")
    if rng.random() < 0.25:            # 25 % con frase distractora
        texto += " " + rng.choice(DISTRACTORES)
    return texto[0].upper() + texto[1:]


def main():
    filas = []
    plan = [("referencia", 10), ("prueba", 8), ("operacion", 4)]
    contador = 1
    for rol, por_clase in plan:
        for causa in CAUSAS:
            for i in range(por_clase):
                filas.append({
                    "id_reporte": f"NC-{contador:03d}",
                    "fecha": f"2026-11-{1 + (contador % 14):02d}",
                    "texto_reporte": armar_reporte(causa, i, rol),
                    "rol": rol,
                    "causa_real": "" if rol == "operacion" else causa,
                    "_causa_oculta": causa,
                    "origen": "SIMULADO_ACADEMICO_NO_REAL",
                })
                contador += 1
    rng.shuffle(filas)
    out = Path(__file__).with_name("reportes_nc_simulados.csv")
    campos = ["id_reporte", "fecha", "texto_reporte", "rol", "causa_real", "origen"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    # Clave de auditoria con la causa de los reportes de operacion (no se sube a Sheets).
    with out.with_name("reportes_nc_simulados_clave.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id_reporte", "_causa_oculta"], extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} reportes -> {out.name}")


if __name__ == "__main__":
    main()
