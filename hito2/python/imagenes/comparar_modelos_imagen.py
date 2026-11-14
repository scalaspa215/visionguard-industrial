"""
VisionGuard Industrial - Hito 2
Comparacion de modelos de imagen sobre el MISMO test (715 imagenes del
dataset publico Casting product image data, Kaggle):

  1. ResNet18 DESPLEGADO   : el mismo resnet18_best.onnx que usa la API de Render
                             (preprocesamiento identico a app.py).
  2. MobileNetV3-Large     : preentrenado ImageNet, ajuste fino.
  3. EfficientNet-B0       : preentrenado ImageNet, ajuste fino.
  4. Umbral simple         : proporcion de pixeles oscuros; umbral elegido en TRAIN.

Ajuste fino (2 y 3): misma particion (train oficial barajado con semilla 42,
80 % entrenamiento / 20 % validacion), Adam lr 1e-4, 224 px, aumento
(volteo + rotacion 10 grados), se guarda la mejor epoca segun VALIDACION.
El test solo se usa al final. Por correr en CPU se usan EPOCAS (por defecto 3)
en vez de las 5 del ResNet18 original: queda documentado como limitacion.

Metricas: accuracy, precision/recall/F1 de la clase Defectuosa, FN, FP,
latencia por imagen en CPU, tamano y McNemar exacto pareado vs ResNet18.
Uso: python comparar_modelos_imagen.py [EPOCAS]
"""
import json
import os
import random
import sys
import time
import urllib.request
from glob import glob
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
import torch.nn as nn
import torchvision.models as tvm
import torchvision.transforms as T
from PIL import Image
from scipy.stats import binomtest
from torch.utils.data import DataLoader, Dataset

AQUI = Path(__file__).parent
EPOCAS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
BASE = Path(os.path.expanduser("~/.cache/kagglehub/datasets/ravirajsinh45/"
                               "real-life-industrial-dataset-of-casting-product/versions/2/casting_data/casting_data"))
ONNX = AQUI / "resnet18_best.onnx"
URL_ONNX = "https://raw.githubusercontent.com/scalaspa215/visionguard-industrial/main/visionguard_api/resnet18_best.onnx"
torch.set_num_threads(max(1, os.cpu_count() - 1))
torch.manual_seed(42)
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]


def listar(split):
    out = []
    for carpeta, y in [("ok_front", 0), ("def_front", 1)]:   # 1 = Defectuosa (igual que la API)
        out += [(p, y) for p in sorted(glob(str(BASE / split / carpeta / "*.jpeg")))]
    return out


train_full, test = listar("train"), listar("test")
random.Random(42).shuffle(train_full)
corte = int(len(train_full) * 0.8)
train, val = train_full[:corte], train_full[corte:]
y_test = np.array([y for _, y in test])
print(f"train {len(train)} · val {len(val)} · test {len(test)}", flush=True)


def metricas(y, p):
    y, p = np.asarray(y), np.asarray(p)
    tp = int(((y == 1) & (p == 1)).sum()); tn = int(((y == 0) & (p == 0)).sum())
    fp = int(((y == 0) & (p == 1)).sum()); fn = int(((y == 1) & (p == 0)).sum())
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return {"accuracy": round((tp + tn) / len(y), 4), "precision_def": round(pr, 4), "recall_def": round(rc, 4),
            "f1_def": round(2 * pr * rc / (pr + rc), 4) if pr + rc else 0.0, "TN": tn, "FP": fp, "FN": fn, "TP": tp}


resultados, predicciones = {}, {}

# ---------- 1. ResNet18 desplegado (ONNX) ----------
if not ONNX.exists():
    urllib.request.urlretrieve(URL_ONNX, ONNX)
ses = ort.InferenceSession(str(ONNX), providers=["CPUExecutionProvider"])
nombre_in = ses.get_inputs()[0].name


def prep_api(p):  # identico a visionguard_api/app.py
    a = np.asarray(Image.open(p).convert("RGB").resize((224, 224), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0
    a = (a - np.array(MEAN, np.float32)) / np.array(STD, np.float32)
    return np.ascontiguousarray(np.transpose(a, (2, 0, 1))[None])


t0 = time.time()
pred = [int(np.argmax(ses.run(None, {nombre_in: prep_api(p)})[0][0])) for p, _ in test]
resultados["ResNet18 (ONNX desplegado)"] = {**metricas(y_test, pred),
                                             "ms_por_imagen_cpu": round((time.time() - t0) / len(test) * 1000, 1),
                                             "tamano_mb": round(ONNX.stat().st_size / 1e6, 1), "parametros_M": 11.18,
                                             "entrenamiento": "Hito 1 (Colab, 5 epocas)"}
predicciones["ResNet18"] = pred
print("ResNet18:", resultados["ResNet18 (ONNX desplegado)"], flush=True)

# ---------- 2. Umbral simple (alternativa de la Navaja de Occam) ----------
def oscuros(p):
    return float((np.asarray(Image.open(p).convert("L").resize((224, 224))) < 60).mean())


f_tr = np.array([oscuros(p) for p, _ in train[:2000]]); y_tr = np.array([y for _, y in train[:2000]])
cands = np.quantile(f_tr, np.linspace(0.01, 0.99, 99))
acc_c = [max(((f_tr > u) == y_tr).mean(), ((f_tr <= u) == y_tr).mean()) for u in cands]
u = cands[int(np.argmax(acc_c))]
signo = ((f_tr > u) == y_tr).mean() >= ((f_tr <= u) == y_tr).mean()
pu = [int((oscuros(p) > u) == signo) for p, _ in test]
resultados["Umbral pixeles oscuros"] = {**metricas(y_test, pu), "umbral": round(float(u), 4),
                                         "ajustado_en": "2000 imagenes de train"}
predicciones["Umbral"] = pu
print("Umbral:", resultados["Umbral pixeles oscuros"], flush=True)

# ---------- 3. Ajuste fino de dos alternativas preentrenadas ----------
tf_tr = T.Compose([T.Resize((224, 224)), T.RandomHorizontalFlip(), T.RandomRotation(10), T.ToTensor(), T.Normalize(MEAN, STD)])
tf_ev = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])


class Casting(Dataset):
    def __init__(self, items, tf): self.items, self.tf = items, tf
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        p, y = self.items[i]
        return self.tf(Image.open(p).convert("RGB")), y


dl = lambda items, tf, sh: DataLoader(Casting(items, tf), batch_size=32, shuffle=sh, num_workers=0)


def evaluar(modelo, loader):
    modelo.eval(); ps = []
    with torch.no_grad():
        for x, _ in loader:
            ps += modelo(x).argmax(1).tolist()
    return ps


def entrenar(nombre, modelo):
    opt = torch.optim.Adam(modelo.parameters(), lr=1e-4); lossf = nn.CrossEntropyLoss()
    dtr, dva, dte = dl(train, tf_tr, True), dl(val, tf_ev, False), dl(test, tf_ev, False)
    mejor, estado, hist, t_ini = -1.0, None, [], time.time()
    for ep in range(EPOCAS):
        modelo.train()
        for x, y in dtr:
            opt.zero_grad(); lossf(modelo(x), y).backward(); opt.step()
        acc = metricas([y for _, y in val], evaluar(modelo, dva))["accuracy"]
        hist.append(acc)
        print(f"  {nombre} epoca {ep + 1}/{EPOCAS}: acc val {acc} ({(time.time() - t_ini) / 60:.1f} min)", flush=True)
        if acc > mejor:
            mejor, estado = acc, {k: v.detach().clone() for k, v in modelo.state_dict().items()}
    modelo.load_state_dict(estado)
    pt = evaluar(modelo, dte)
    x1 = tf_ev(Image.open(test[0][0]).convert("RGB"))[None]
    modelo.eval(); t1 = time.time()
    with torch.no_grad():
        for _ in range(30):
            modelo(x1)
    resultados[nombre] = {**metricas(y_test, pt), "ms_por_imagen_cpu": round((time.time() - t1) / 30 * 1000, 1),
                          "parametros_M": round(sum(p.numel() for p in modelo.parameters()) / 1e6, 2),
                          "mejor_acc_val": mejor, "acc_val_por_epoca": hist, "epocas": EPOCAS,
                          "minutos_entrenamiento_cpu": round((time.time() - t_ini) / 60, 1)}
    predicciones[nombre] = pt
    print(nombre, resultados[nombre], flush=True)


m = tvm.mobilenet_v3_large(weights=tvm.MobileNet_V3_Large_Weights.IMAGENET1K_V2)
m.classifier[3] = nn.Linear(m.classifier[3].in_features, 2)
entrenar("MobileNetV3-Large", m)
m = tvm.efficientnet_b0(weights=tvm.EfficientNet_B0_Weights.IMAGENET1K_V1)
m.classifier[1] = nn.Linear(m.classifier[1].in_features, 2)
entrenar("EfficientNet-B0", m)

# ---------- 4. McNemar pareado vs ResNet18 ----------
ref = np.array(predicciones["ResNet18"]) == y_test
mcnemar = {}
for k in ["MobileNetV3-Large", "EfficientNet-B0", "Umbral"]:
    otro = np.array(predicciones[k]) == y_test
    b, c = int((ref & ~otro).sum()), int((~ref & otro).sum())
    mcnemar[k] = {"resnet_acierta_otro_falla": b, "otro_acierta_resnet_falla": c,
                  "p_valor": round(binomtest(b, b + c, 0.5).pvalue, 4) if b + c else 1.0}
salida = {"dataset": "Casting product image data (Kaggle, ravirajsinh45) - test oficial 715 imagenes",
          "clase_positiva": "Defectuosa", "resultados": resultados, "mcnemar_vs_resnet18": mcnemar}
(AQUI / "resultados_imagenes.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
with (AQUI / "predicciones_imagenes.csv").open("w", encoding="utf-8") as f:
    f.write("archivo,real," + ",".join(predicciones) + "\n")
    for i, (p, y) in enumerate(test):
        f.write(f"{Path(p).name},{y}," + ",".join(str(predicciones[k][i]) for k in predicciones) + "\n")
print(json.dumps(mcnemar, indent=1))
