"""Genera VisionGuard_Hito2_Comparaciones_Colab.ipynb (ejecutar el .ipynb en Colab con GPU)."""
from pathlib import Path
import nbformat as nbf

nb = nbf.v4.new_notebook()
md = lambda s: nbf.v4.new_markdown_cell(s)
code = lambda s: nbf.v4.new_code_cell(s)
REPO_RAW = "https://raw.githubusercontent.com/scalaspa215/visionguard-industrial/main"

nb.cells = [
md("""# VisionGuard Industrial · Hito 2 · Comparación de modelos (Navaja de Occam)

Ejecutar en **Google Colab con GPU** (Entorno de ejecución → Cambiar tipo → T4 GPU), en orden.

| Parte | Modelo | Alternativa | Mismos datos de prueba |
|---|---|---|---|
| A | ResNet18 (ONNX desplegado) | EfficientNet-B0 y MobileNetV3-Large preentrenados + umbral simple | 715 imágenes `test` del dataset Casting (Kaggle) |
| B | Transformer de embeddings multilingüe (MiniLM-L12) | Reglas fijas de palabras clave | 40 reportes NC simulados `prueba` |
| C | GRU (API desplegada) | Ingenuo, promedio móvil, SES, Holt, Holt-Winters, regresión | 81 días `test` (datos simulados) |

**Reglas:** no se ajusta nada con los datos de prueba; todas las cifras se imprimen desde el código. Si un modelo complejo no gana, se reporta tal cual.
"""),
md("## A · Imágenes: ResNet18 vs otros dos modelos preentrenados"),
code("""!pip -q install kagglehub onnxruntime
import kagglehub, os, glob, random, time, json
import numpy as np, torch, torch.nn as nn
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import torchvision.models as tvm

# Dataset publico: Casting product image data for quality inspection (Kaggle, ravirajsinh45).
# Si kagglehub pide credenciales: subir kaggle.json (Kaggle > Settings > API) a /root/.kaggle/.
ruta = kagglehub.dataset_download('ravirajsinh45/real-life-industrial-dataset-of-casting-product')
base = glob.glob(os.path.join(ruta, '**', 'casting_data'), recursive=True)[0]
def listar(split):
    out = []
    for carpeta, etiqueta in [('ok_front', 0), ('def_front', 1)]:   # 1 = Defectuosa (igual que la API)
        out += [(p, etiqueta) for p in sorted(glob.glob(os.path.join(base, split, carpeta, '*.jpeg')))]
    return out
train_full, test = listar('train'), listar('test')
random.Random(42).shuffle(train_full)
corte = int(len(train_full) * 0.8)
train, val = train_full[:corte], train_full[corte:]
print('train', len(train), 'val', len(val), 'test', len(test))   # Hito 1: 5306 / 1327 / 715
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'; print('dispositivo:', DEV)"""),
code("""MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
tf_train = T.Compose([T.Resize((224, 224)), T.RandomHorizontalFlip(), T.RandomRotation(10), T.ToTensor(), T.Normalize(MEAN, STD)])
tf_eval = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
class Casting(Dataset):
    def __init__(self, items, tf): self.items, self.tf = items, tf
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        p, y = self.items[i]; return self.tf(Image.open(p).convert('RGB')), y
dl = lambda items, tf, sh: DataLoader(Casting(items, tf), batch_size=32, shuffle=sh, num_workers=2)
dl_train, dl_val, dl_test = dl(train, tf_train, True), dl(val, tf_eval, False), dl(test, tf_eval, False)

def metricas(y, p):
    y, p = np.array(y), np.array(p)
    tp = int(((y == 1) & (p == 1)).sum()); tn = int(((y == 0) & (p == 0)).sum())
    fp = int(((y == 0) & (p == 1)).sum()); fn = int(((y == 1) & (p == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else 0; rec = tp / (tp + fn) if tp + fn else 0
    return dict(accuracy=round((tp + tn) / len(y), 4), precision_def=round(prec, 4), recall_def=round(rec, 4),
                f1_def=round(2 * prec * rec / (prec + rec), 4) if prec + rec else 0, TN=tn, FP=fp, FN=fn, TP=tp)
resultados, predicciones = {}, {}
y_test = [y for _, y in test]"""),
code(f"""# A1. ResNet18 DESPLEGADO (mismo ONNX que usa la API de Render) sobre el test
import onnxruntime as ort, urllib.request
urllib.request.urlretrieve('{REPO_RAW}/visionguard_api/resnet18_best.onnx', 'resnet18_best.onnx')
ses = ort.InferenceSession('resnet18_best.onnx', providers=['CPUExecutionProvider'])
def prep_api(p):  # identico a app.py: resize bilinear 224, /255, normalizacion ImageNet, CHW
    a = np.asarray(Image.open(p).convert('RGB').resize((224, 224), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0
    a = (a - np.array(MEAN, np.float32)) / np.array(STD, np.float32)
    return np.ascontiguousarray(np.transpose(a, (2, 0, 1))[None])
t0 = time.time(); pred = []
for p, _ in test:
    pred.append(int(np.argmax(ses.run(None, {{ses.get_inputs()[0].name: prep_api(p)}})[0][0])))
lat = (time.time() - t0) / len(test) * 1000
resultados['ResNet18 (ONNX desplegado)'] = dict(**metricas(y_test, pred), ms_por_imagen_cpu=round(lat, 1),
                                                 tamano_mb=round(os.path.getsize('resnet18_best.onnx') / 1e6, 1))
predicciones['ResNet18'] = pred
print(resultados['ResNet18 (ONNX desplegado)'])"""),
code("""# A2. Ajuste fino de dos alternativas preentrenadas con la MISMA receta (5 epocas, Adam 1e-4, 224 px)
def entrenar(nombre, modelo, epocas=5):
    torch.manual_seed(42); modelo = modelo.to(DEV)
    opt = torch.optim.Adam(modelo.parameters(), lr=1e-4); lossf = nn.CrossEntropyLoss()
    mejor, estado = -1, None
    for ep in range(epocas):
        modelo.train()
        for x, y in dl_train:
            opt.zero_grad(); lossf(modelo(x.to(DEV)), y.to(DEV)).backward(); opt.step()
        modelo.eval(); yv, pv = [], []
        with torch.no_grad():
            for x, y in dl_val: pv += modelo(x.to(DEV)).argmax(1).cpu().tolist(); yv += y.tolist()
        acc = metricas(yv, pv)['accuracy']; print(f'{nombre} epoca {ep+1}: acc val {acc}')
        if acc > mejor: mejor, estado = acc, {k: v.detach().clone() for k, v in modelo.state_dict().items()}
    modelo.load_state_dict(estado); modelo.eval()          # mejor epoca segun VALIDACION
    pt = []; t0 = time.time()
    with torch.no_grad():
        for x, _ in dl_test: pt += modelo(x.to(DEV)).argmax(1).cpu().tolist()
    cpu = modelo.to('cpu'); x1 = tf_eval(Image.open(test[0][0]).convert('RGB'))[None]
    t1 = time.time()
    with torch.no_grad():
        for _ in range(50): cpu(x1)
    params = sum(p.numel() for p in cpu.parameters()) / 1e6
    resultados[nombre] = dict(**metricas(y_test, pt), ms_por_imagen_cpu=round((time.time() - t1) / 50 * 1000, 1),
                              parametros_M=round(params, 2), mejor_acc_val=mejor)
    predicciones[nombre] = pt; print(resultados[nombre])

m = tvm.efficientnet_b0(weights=tvm.EfficientNet_B0_Weights.IMAGENET1K_V1)
m.classifier[1] = nn.Linear(m.classifier[1].in_features, 2); entrenar('EfficientNet-B0', m)
m = tvm.mobilenet_v3_large(weights=tvm.MobileNet_V3_Large_Weights.IMAGENET1K_V2)
m.classifier[3] = nn.Linear(m.classifier[3].in_features, 2); entrenar('MobileNetV3-Large', m)"""),
code("""# A3. Alternativa simple: umbral sobre proporcion de pixeles oscuros (umbral elegido en TRAIN)
def oscuros(p): return float((np.asarray(Image.open(p).convert('L').resize((224, 224))) < 60).mean())
f_tr = np.array([oscuros(p) for p, _ in train[:1500]]); y_tr = np.array([y for _, y in train[:1500]])
cands = np.quantile(f_tr, np.linspace(0.01, 0.99, 99))
mejor_u = max(cands, key=lambda u: max(((f_tr > u) == y_tr).mean(), ((f_tr <= u) == y_tr).mean()))
signo = ((f_tr > mejor_u) == y_tr).mean() >= ((f_tr <= mejor_u) == y_tr).mean()
pu = [int((oscuros(p) > mejor_u) == signo) for p, _ in test]
resultados['Umbral pixeles oscuros'] = metricas(y_test, pu); predicciones['Umbral'] = pu
print(resultados['Umbral pixeles oscuros'])"""),
code("""# A4. Tabla final + McNemar (diferencia de errores pareados vs ResNet18 sobre las mismas 715 imagenes)
import pandas as pd
from scipy.stats import binomtest
tabla = pd.DataFrame(resultados).T; display(tabla)
ref = np.array(predicciones['ResNet18']) == np.array(y_test)
for k in ['EfficientNet-B0', 'MobileNetV3-Large', 'Umbral']:
    otro = np.array(predicciones[k]) == np.array(y_test)
    b, c = int((ref & ~otro).sum()), int((~ref & otro).sum())
    pval = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    print(f'McNemar ResNet18 vs {k}: ResNet acierta/otro falla={b}, al reves={c}, p={pval:.4f}')
tabla.to_csv('comparacion_imagenes.csv')
print('Criterio de eleccion: menor FN (pieza defectuosa aprobada) > F1 defectuosa > latencia CPU (Render sin GPU).')"""),
md("## B · Texto: Transformer de embeddings vs reglas fijas"),
code(f"""!pip -q install sentence-transformers
for f in ['nlp_comun.py', 'evaluar_nlp.py', 'reportes_nc_simulados.csv', 'generar_reportes_nc.py']:
    urllib.request.urlretrieve('{REPO_RAW}/hito2/python/nlp/' + f, f)
!python evaluar_nlp.py"""),
md("## C · Series temporales: GRU (API) vs modelos clásicos"),
code(f"""for f in ['comparar_series.py', 'tasa_defectos_diaria_SIMULADA.csv']:
    urllib.request.urlretrieve('{REPO_RAW}/hito2/python/series/' + f, f)
!python comparar_series.py"""),
md("""## Interpretación (completar con las cifras impresas arriba)
- **Imágenes:** ¿qué modelo tiene menos falsos negativos en el test? Si EfficientNet/MobileNet no superan a ResNet18 de forma significativa (McNemar p ≥ 0,05), se mantiene ResNet18 por ser el ya desplegado y validado.
- **Texto:** comparar F1 macro del Transformer vs reglas en los 40 reportes de prueba. Recordar que los reportes son simulados.
- **Series:** el GRU no supera al promedio móvil ni al SES en prueba; se conserva como componente demostrativo y se discute (Navaja de Occam).
"""),
]
nb.metadata = {"accelerator": "GPU", "colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"}}
salida = Path(__file__).with_name("VisionGuard_Hito2_Comparaciones_Colab.ipynb")
nbf.write(nb, salida)
print("OK", salida.name)
