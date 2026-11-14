"""VisionGuard Industrial — dashboard académico de control de calidad."""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="VisionGuard Industrial", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.stApp {background:#090f1c;color:#e9f3ff}
[data-testid="stSidebar"] {background:#101c2c}
.block-container {padding-top:1.3rem;max-width:1450px}
[data-testid="stMetric"] {background:linear-gradient(135deg,#17273d,#101a2a);border:1px solid #2e415b;border-radius:15px;padding:15px}
[data-testid="stMetricLabel"] {color:#9ebbd8}
[data-testid="stMetricValue"] {color:#fff}
.hero {background:linear-gradient(115deg,#173657,#101b2f);padding:22px 26px;border:1px solid #325773;border-radius:16px;margin-bottom:22px}
.hero h1 {color:#fff;margin:3px 0;font-size:2.1rem}
.hero p {color:#adc9e6;margin-bottom:0}
.eyebrow {letter-spacing:2px;font-size:12px;color:#48d6df;font-weight:700}
</style>
""", unsafe_allow_html=True)

REQUIRED = ['archivo', 'clasificacion', 'confianza', 'prioridad', 'estado', 'fecha_registro']


def demo_data():
    """Muestra ilustrativa; nunca representar como telemetría industrial real."""
    return pd.DataFrame([
        dict(archivo='VG_TEST_013.jpeg', fecha_registro='2026-11-13 15:23:22', clasificacion='Defectuosa', confianza=.9994,
             prioridad='alta', linea_mayor_pronostico='L3', pronostico_max_pct=7.89, casos_nlp=4,
             estado='PENDIENTE_VALIDACION_HUMANA', validacion_humana_realizada=False),
        dict(archivo='VG_TEST_014.jpeg', fecha_registro='2026-11-13 17:21:57', clasificacion='Defectuosa', confianza=.9994,
             prioridad='alta', linea_mayor_pronostico='L3', pronostico_max_pct=7.89, casos_nlp=4,
             estado='PENDIENTE_VALIDACION_HUMANA', validacion_humana_realizada=False),
        dict(archivo='VG_TEST_015.jpeg', fecha_registro='2026-11-13 18:31:30', clasificacion='Defectuosa', confianza=.9949,
             prioridad='alta', linea_mayor_pronostico='L3', pronostico_max_pct=7.89, casos_nlp=4,
             estado='ACCION_RECHAZADA_POR_HUMANO', validacion_humana_realizada=True),
    ])


@st.cache_data(ttl=60, show_spinner=False)
def google_data():
    import gspread
    creds = dict(st.secrets['gcp_service_account'])
    sheet_id = st.secrets['sheets']['spreadsheet_id']
    sheet_name = st.secrets['sheets'].get('worksheet', 'Analisis_Integrado')
    worksheet = gspread.service_account_from_dict(creds).open_by_key(sheet_id).worksheet(sheet_name)
    return pd.DataFrame(worksheet.get_all_records())


def bool_value(v):
    return str(v).strip().lower() in {'true', '1', 'sí', 'si', 'yes', 'verdadero'}


def normalize(raw):
    d = raw.copy()
    optional = ['linea_mayor_pronostico', 'pronostico_max_pct', 'casos_nlp', 'validacion_humana_realizada', 'diagnostico', 'recomendacion']
    for col in REQUIRED + optional:
        if col not in d:
            d[col] = None
    for col in ['confianza', 'pronostico_max_pct', 'casos_nlp']:
        d[col] = pd.to_numeric(d[col], errors='coerce')
    d['fecha_registro'] = pd.to_datetime(d['fecha_registro'], errors='coerce')
    d['validacion_humana_realizada'] = d['validacion_humana_realizada'].map(bool_value)
    for col in ['archivo', 'clasificacion', 'prioridad', 'estado', 'linea_mayor_pronostico']:
        d[col] = d[col].fillna('Sin dato').astype(str)
    return d


def style_chart(fig, height=320):
    fig.update_layout(height=height, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#dbe8fa'), margin=dict(l=14, r=14, t=16, b=15),
                      legend=dict(orientation='h', y=-.24))
    fig.update_xaxes(gridcolor='#293b56')
    fig.update_yaxes(gridcolor='#293b56')
    return fig


st.sidebar.title('🛡️ VisionGuard')
st.sidebar.caption('AI QUALITY CONTROL · CONTROL CENTER')
# Importante: los secretos se configuran SOLO en Streamlit, nunca en el repositorio público.
try:
    configured = 'gcp_service_account' in st.secrets and 'sheets' in st.secrets
except Exception:
    configured = False

source = st.sidebar.radio('Fuente de datos', ['Demostración', 'Cargar CSV', 'Google Sheets (privado)'], index=2 if configured else 0)
raw = pd.DataFrame()
if source == 'Demostración':
    raw = demo_data()
    st.sidebar.info('Datos académicos ilustrativos. No son mediciones de una planta industrial.')
elif source == 'Cargar CSV':
    uploaded = st.sidebar.file_uploader('CSV exportado de Analisis_Integrado', type='csv')
    if uploaded:
        try:
            raw = pd.read_csv(uploaded)
        except Exception as exc:
            st.sidebar.error(f'No se pudo leer el CSV: {type(exc).__name__}')
else:
    if not configured:
        st.sidebar.warning('Debes configurar gcp_service_account y sheets en Streamlit Secrets.')
    else:
        try:
            raw = google_data()
            st.sidebar.success('Conectado a Google Sheets')
        except Exception:
            st.sidebar.error('No se pudo conectar a Sheets. Comprueba los Secrets y permisos.')

if st.sidebar.button('🔄 Actualizar datos'):
    st.cache_data.clear()
    st.rerun()

df = normalize(raw)
st.sidebar.divider()
if not df.empty:
    classes = sorted(df['clasificacion'].unique())
    selected = st.sidebar.multiselect('Filtrar por clasificación', classes, default=classes)
    df = df[df['clasificacion'].isin(selected)]
    priorities = sorted(df['prioridad'].unique())
    selected_p = st.sidebar.multiselect('Filtrar por prioridad', priorities, default=priorities)
    df = df[df['prioridad'].isin(selected_p)]

st.markdown('''<div class="hero"><div class="eyebrow">VISIONGUARD INDUSTRIAL · v2.1</div>
<h1>Centro de Control Inteligente</h1><p>Visión artificial · GRU · NLP · IA generativa · Supervisión humana</p></div>''', unsafe_allow_html=True)

if source == 'Demostración':
    st.info('**Modo demostración:** 3 registros académicos ilustrativos. Los pronósticos GRU son simulados, no mediciones reales.')
if df.empty:
    st.warning('Sin registros disponibles. Revisa el origen de datos o los filtros.')
    st.stop()

n = len(df)
defects = int(df['clasificacion'].str.casefold().eq('defectuosa').sum())
human = int(df['validacion_humana_realizada'].sum())
conf = df['confianza'].mean()
if pd.notna(conf) and conf > 1:
    conf /= 100  # compatibilidad cuando la fuente trae 99.4 y no 0.994

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('Inspecciones', n)
c2.metric('Piezas defectuosas', defects)
c3.metric('Tasa de defectos', f'{100*defects/n:.1f}%')
c4.metric('Revisiones humanas', human)
c5.metric('Confianza promedio', f'{conf*100:.2f}%' if pd.notna(conf) else '—')

t1, t2, t3, t4, t5 = st.tabs(['📊 Operaciones', '🧠 ResNet18 + NLP', '📈 GRU', '👤 Validación humana', '📋 Historial'])
with t1:
    a,b = st.columns(2)
    with a:
        st.subheader('Clasificación de piezas')
        vc = df['clasificacion'].value_counts().rename_axis('clase').reset_index(name='n')
        fig = px.pie(vc, names='clase', values='n', hole=.62,
                     color_discrete_sequence=['#20cbd1', '#f1b75c', '#7099ef'])
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with b:
        st.subheader('Prioridad de inspección')
        vc = df['prioridad'].value_counts().rename_axis('prioridad').reset_index(name='n')
        fig = px.bar(vc, x='prioridad', y='n', color='prioridad', color_discrete_sequence=['#20cbd1','#7099ef','#f1b75c'])
        st.plotly_chart(style_chart(fig), use_container_width=True)
    st.caption('Los porcentajes se calculan sobre el historial filtrado, no sobre la producción total de una fábrica.')

with t2:
    st.subheader('Resultados experimentales ResNet18')
    st.caption('Conjunto independiente de 715 imágenes, no las tres inspecciones del dashboard.')
    a,b,c,d = st.columns(4)
    a.metric('Accuracy', '97,76%')
    b.metric('Precision defectuosa', '99,32%')
    c.metric('Recall defectuosa', '97,12%')
    d.metric('F1-score defectuosa', '98,21%')
    cm = pd.DataFrame([[259,3],[13,440]], index=['Real correcta','Real defectuosa'],
                      columns=['Pred. correcta','Pred. defectuosa'])
    fig = px.imshow(cm, text_auto=True, color_continuous_scale=['#12253a','#1fd0c7'])
    st.plotly_chart(style_chart(fig, 350), use_container_width=True)
    st.subheader('NLP integrado')
    count_nlp = int(df['casos_nlp'].max()) if df['casos_nlp'].notna().any() else 0
    st.metric('Casos NLP referenciados', count_nlp)
    st.caption('Este contador no evalúa la precisión ni verifica por sí solo el funcionamiento del Transformer.')

with t3:
    st.subheader('Análisis predictivo GRU')
    st.warning('Los valores de pronóstico provienen de una demostración simulada; no son tasas reales observadas.')
    pred = df.dropna(subset=['pronostico_max_pct']).copy()
    if not pred.empty:
        grouped = pred.groupby('linea_mayor_pronostico', as_index=False)['pronostico_max_pct'].mean()
        fig = px.bar(grouped, x='linea_mayor_pronostico', y='pronostico_max_pct', color='linea_mayor_pronostico',
                     color_discrete_sequence=['#20cbd1','#749bf5','#ecb45f'])
        fig.update_layout(xaxis_title='Línea de mayor pronóstico',yaxis_title='Pronóstico (%)')
        st.plotly_chart(style_chart(fig), use_container_width=True)
    st.markdown('**Comparación de referencia de la API académica (/pronosticos-demo, 2026-10-28)**')
    st.dataframe(pd.DataFrame({'Línea':['L1','L2','L3'], 'GRU (%)':[4.09,6.48,7.89],
                               'Promedio móvil (%)':[4.57,8.05,7.83]}), hide_index=True, use_container_width=True)

with t4:
    st.subheader('Decisiones de supervisión humana')
    approved = int(df['estado'].str.contains('AUTORIZADA_POR_HUMANO',case=False,na=False).sum())
    rejected = int(df['estado'].str.contains('RECHAZADA_POR_HUMANO',case=False,na=False).sum())
    a,b,c = st.columns(3)
    a.metric('Acciones autorizadas', approved)
    b.metric('Acciones rechazadas', rejected)
    c.metric('Pendientes de revisión', int((~df['validacion_humana_realizada']).sum()))
    vc = df['estado'].value_counts().rename_axis('estado').reset_index(name='inspecciones')
    fig = px.bar(vc, x='inspecciones', y='estado', orientation='h', color_discrete_sequence=['#1bc7d0'])
    st.plotly_chart(style_chart(fig, 315), use_container_width=True)
    st.caption('Autorizar una acción NO equivale a certificar que la pieza esté libre de defectos.')

with t5:
    st.subheader('Historial de inspecciones')
    cols=['fecha_registro','archivo','clasificacion','confianza','prioridad','linea_mayor_pronostico',
          'pronostico_max_pct','casos_nlp','estado','validacion_humana_realizada']
    st.dataframe(df[cols].sort_values('fecha_registro', ascending=False), hide_index=True, use_container_width=True)
    st.download_button('⬇️ Exportar CSV', df.to_csv(index=False).encode('utf-8-sig'),
                       file_name='visionguard_historial.csv', mime='text/csv')
    choice=st.selectbox('Ver detalle de inspección',df['archivo'].tolist())
    row=df[df['archivo']==choice].iloc[0]
    st.markdown('**Diagnóstico IA**')
    st.write(row['diagnostico'] if pd.notna(row['diagnostico']) else 'No disponible en esta fuente')
    st.markdown('**Recomendación**')
    st.write(row['recomendacion'] if pd.notna(row['recomendacion']) else 'No disponible en esta fuente')

st.divider()
st.caption('VisionGuard Industrial · Prototipo académico. La IA apoya el control de calidad y no sustituye la decisión humana.')
