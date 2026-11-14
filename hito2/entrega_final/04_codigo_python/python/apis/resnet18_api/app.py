
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from pathlib import Path
import onnxruntime as ort
import numpy as np
import io

app = FastAPI(title="VisionGuard Industrial API")

MODEL_PATH = Path(__file__).parent / "resnet18_best.onnx"

session = ort.InferenceSession(
    str(MODEL_PATH),
    providers=["CPUExecutionProvider"]
)

CLASES = ["Correcta", "Defectuosa"]

@app.get("/health")
def health():
    return {"status": "ok", "model": "ResNet18 ONNX"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contenido = await file.read()

    if len(contenido) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="La imagen supera los 10 MB"
        )

    try:
        imagen = Image.open(
            io.BytesIO(contenido)
        ).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Archivo de imagen no valido"
        )

    # Preprocesamiento usado en entrenamiento
    imagen = imagen.resize(
        (224, 224),
        Image.Resampling.BILINEAR
    )

    array = np.asarray(
        imagen, dtype=np.float32
    ) / 255.0

    mean = np.array(
        [0.485, 0.456, 0.406], dtype=np.float32
    )
    std = np.array(
        [0.229, 0.224, 0.225], dtype=np.float32
    )

    array = (array - mean) / std
    array = np.transpose(array, (2, 0, 1))
    array = np.expand_dims(array, axis=0)
    array = np.ascontiguousarray(array)

    # Prediccion de ResNet18
    entrada = session.get_inputs()[0].name
    logits = session.run(
        None, {entrada: array}
    )[0][0]

    # Convertir resultados a probabilidades
    logits = logits.astype(np.float64)
    exp = np.exp(logits - np.max(logits))
    probabilidades = exp / exp.sum()

    clase_id = int(np.argmax(probabilidades))
    confianza = float(probabilidades[clase_id])

    revision = confianza < 0.90

    if revision:
        decision = "REVISION_MANUAL"
    elif clase_id == 1:
        decision = "APARTAR_PIEZA"
    else:
        decision = "APROBACION_PROVISIONAL"

    return {
        "archivo": file.filename,
        "modelo": "ResNet18",
        "clasificacion": CLASES[clase_id],
        "confianza": round(confianza, 4),
        "probabilidades": {
            "correcta": round(float(probabilidades[0]), 4),
            "defectuosa": round(float(probabilidades[1]), 4)
        },
        "decision_sugerida": decision,
        "requiere_revision_humana": revision,
        "advertencia": "Prediccion automatizada; no sustituye la inspeccion humana"
    }
