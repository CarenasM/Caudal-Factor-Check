import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(page_title="Configurador Waldner SAT", layout="wide")

# --- ESTILOS CSS ACTUALIZADOS (Letras más pequeñas y Botón Azul) ---
st.markdown("""
    <style>
    /* Reducción general de etiquetas */
    .w-label {
        font-family: 'Arial', sans-serif;
        font-size: 18px; /* Reducido de 24px */
        font-style: italic;
        margin-bottom: -10px;
    }
    
    /* Cuadro de Caudal más compacto */
    .w-caudal {
        background-color: #90EE90;
        color: #2e7d32;
        font-size: 20px; /* Reducido de 26px */
        font-weight: bold;
        text-align: center;
        padding: 8px 15px;
        border-radius: 5px;
        border: 2px solid #2e7d32;
    }
    
    /* Cuadros de Factores más pequeños */
    .w-factor {
        background-color: #E3F2FD;
        color: #1976D2;
        font-size: 16px; /* Reducido de 22px */
        font-weight: bold;
        text-align: center;
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #2196F3;
    }
    .w-factor-val {
        font-size: 22px; /* Reducido de 28px */
        display: block;
    }
    
    /* Cuadro de Xtras compacto */
    .w-xtras-container {
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 5px;
        background-color: #fafafa;
        margin-top: 10px;
    }
    .w-xtras-title {
        color: red;
        font-style: italic;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
    }
    .w-xtras-text {
        font-size: 13px;
        text-align: center;
    }

    /* Estilo para los botones de Serie */
    div.stButton > button {
        font-size: 14px !important;
        padding: 5px !important;
        border: 1px solid #999 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    if not os.path.exists(EXCEL_FILE): return None
    try:
        df = pd.read_excel(EXCEL_FILE)
        df.columns = [str(c).strip().lower() for c in df.columns]
        df = df.fillna("N/A").astype(str)
        # Soporte para versiones nuevas y viejas de Pandas
        f_limpiar = lambda x: str(x).strip()
        df = df.map(f_limpiar) if hasattr(df, 'map') else df.applymap(f_limpiar)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = cargar_datos()
if df is None:
    st.error("Archivo no encontrado o error en Excel."); st.stop()

st.write("Seleccione parámetros para acceder a la información")

# --- 1. BOTONES DE SERIE (Con cambio a AZUL al seleccionar) ---
st.markdown('<p class="w-label">Serie</p>', unsafe_allow_html=True)
series_disponibles = sorted(df['serie'].unique())

if "serie_sel" not in st.session_state:
    st.session_state.serie_sel = series_disponibles[0]

cols_s = st.columns(len(series_disponibles))
for i, s in enumerate(series_disponibles):
    # Si la serie es la seleccionada, el botón se vuelve azul
    es_seleccionado = st.session_state.serie_sel == s
    tipo = "primary" if es_seleccionado else "secondary"
    
    if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True, type=tipo):
        st.session_state.serie_sel = s
        st.rerun()

# --- 2. FILTROS Y RESULTADOS ---
col_izq, col_der = st.columns([1, 2])

with col_izq:
    df_f = df[df['serie'] == st.session_state.serie_sel]
    
    st.markdown('<p class="w-label">Dimensión</p>', unsafe_allow_html=True)
    dim_opts = sorted(df_f['dimension'].unique(), key=lambda x: int(x) if x.isdigit() else 0)
    sel_dim = st.selectbox("dim", dim_opts, label_visibility="collapsed")
    st.caption("mm")
    df_f = df_f[df_f['dimension'] == sel_dim]
    
    st.markdown('<p class="w-label">Modelo</p>', unsafe_allow_html=True)
    mod_opts = sorted(df_f['modelo'].unique())
    sel_mod = st.selectbox("mod", mod_opts, label_visibility="collapsed")
    df_f = df_f[df_f['modelo'] == sel_mod]
    
    st.markdown('<p class="w-label">Año</p>', unsafe_allow_html=True)
    ano_opts = df_f['año'].unique()
    sel_ano = st.selectbox("ano", ano_opts, label_visibility="collapsed")
    df_f = df_f[df_f['año'] == sel_ano]

with col_der:
    if not df_f.empty:
        res = df_f.iloc[0]
        
        # Caudal (Derecha arriba)
        st.markdown(f"""
            <div style="
