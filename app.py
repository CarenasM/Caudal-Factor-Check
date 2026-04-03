import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(page_title="Caudales & Factor Check", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main-title {
        font-family: sans-serif;
        color: #0D47A1;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .w-label { 
        font-family: sans-serif; 
        font-size: 15px; 
        font-style: italic; 
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
    }
    .caudal-container {
        height: 50px;
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .w-caudal {
        background-color: #90EE90; color: #1b5e20;
        font-size: 20px; font-weight: bold; text-align: center;
        padding: 5px 12px; border-radius: 8px; border: 2px solid #2e7d32;
        display: inline-block;
    }
    
    /* Cuadros de Factores REDUCIDOS para que quepan bajo las fotos */
    .w-factor {
        background-color: #E3F2FD; color: #0D47A1;
        font-size: 12px; font-weight: bold; text-align: center;
        padding: 5px; border-radius: 8px; border: 1px solid #2196F3;
        margin-top: 5px;
        width: 100%;
    }
    .w-factor-val { font-size: 16px; display: block; margin-top: 2px; }
    
    .stImage > img {
        border-radius: 10px;
        border: 1px solid #ddd;
    }

    .w-xtras-container {
        border: 1px solid #333; padding: 10px; border-radius: 5px;
        background-color: #fff; margin-top: 15px;
    }
    .w-xtras-title { color: red; font-style: italic; font-weight: bold; font-size: 13px; text-align: center; margin-bottom: 2px; }
    .w-xtras-text { font-size: 12px; text-align: center; color: #333; }
    
    div.stButton > button[kind="primary"] {
        background-color: #00BFFF !important; 
        color: white !important;
        border: 1px solid #00BFFF !important;
    }
    div.stButton > button { font-size: 13px !important; padding: 2px !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    if not os.path.exists(EXCEL_FILE): return None
    try:
        df = pd.read_excel(EXCEL_FILE)
        df.columns = [str(c).strip().lower() for c in df.columns]
        df = df.fillna("N/A").astype(str)
        f_limpiar = lambda x: str(x).strip()
        df = df.map(f_limpiar) if hasattr(df, 'map') else df.applymap(f_limpiar)
        return df
    except Exception as e:
        st.error(f"Error: {e}"); return None

df = cargar_datos()
if df is None: st.stop()

st.sidebar.markdown("---")
st.sidebar.write("🛠️ **Soporte Técnico SAT**")
st.sidebar.markdown("By **C@renasM**")

st.markdown('<p class="main-title">Caudales & Factor Check</p>', unsafe_allow_html=True)
st.write("Seleccione parámetros")

# --- 1. BOTONES DE SERIE ---
series_disponibles = sorted(df['serie'].unique())
if "serie_sel" not in st.session_state: st.session_state.serie_sel = None

cols_s = st.columns(len(series_disponibles))
for i, s in enumerate(series_disponibles):
    es_activo = "primary" if st.session_state.serie_sel == s else "secondary"
    if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True, type=es_activo):
        st.session_state.serie_sel = s
        st.rerun()

# --- 2. FLUJO DE SELECCIÓN ---
if st.session_state.serie_sel:
    col_izq, col_der = st.columns([1, 2])
    with col_izq:
        df_f = df[df['serie'] == st.session_state.serie_sel]
        st.markdown('<p class="w-label">Dimensión (mm)</p>', unsafe_allow_html=True)
        dim_opts = ["- Seleccionar -"] + sorted(df_f['dimension'].unique().tolist(), key=lambda x: int(x) if str(x).isdigit() else 0)
        sel_dim = st.selectbox("dim", dim_opts, label_visibility="collapsed")
        
        if sel_dim != "- Seleccionar -":
            df_f = df_f[df_f['dimension'] == sel_dim]
            st.markdown('<p class="w-label">Modelo</p>', unsafe_allow_html=True)
            mod_opts = ["- Seleccionar -"] + sorted(df_f['modelo'].unique().tolist())
            sel_mod = st.selectbox("mod", mod_opts, label_visibility="collapsed")
            
            if sel_mod != "- Seleccionar -":
                df_f = df_f[df_f['modelo'] == sel_mod]
                st.markdown('<p class="w-label">Año</p>', unsafe_allow_html=True)
                ano_opts = ["- Seleccionar -"] + df_f['año'].unique().tolist()
                sel_ano = st.selectbox("ano", ano_opts, label_visibility="collapsed")
                if sel_ano != "- Seleccionar -":
                    df_f = df_f[df_f['año'] == sel_ano]

    with col_der:
        if 'sel_ano' in locals() and sel_ano != "- Seleccionar -" and not df_f.empty:
            res = df_f.iloc[0]
            
            # --- CAUDAL SUPERIOR ---
            st.markdown(f"""
                <div class="caudal-container">
                    <span style="margin-right: 10px; font-weight: bold; font-size: 13px;">Caudal Consigna</span>
                    <div class="w-caudal">{res['consigna']}</div>
                </div>
            """, unsafe_allow_html=True)

            # --- FOTOS Y FACTORES ALINEADOS ---
            # Usamos 4 columnas para que las fotos queden centradas y los textos justo debajo
            f_cols = st.columns([1, 1, 0.5, 0.5])
            
            with f_cols[0]: # COLUMNA BYPASS
                if os.path.exists("fotos/bypass.jpg"):
                    st.image("fotos/bypass.jpg", use_container_width=True)
                st.markdown(f'<div class="w-factor">Bypass<br><span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
                    
            with f_cols[1]: # COLUMNA LOWER
                if os.path.exists("fotos/lower.jpg"):
                    st.image("fotos/lower.jpg", use_container_width=True)
                st.markdown(f'<div class="w-factor">Lower<br><span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
            
            # --- XTRAS ---
            st.markdown(f"""
                <div class="w-xtras-container">
                    <div class="w-xtras-title">Xtras</div>
                    <div class="w-xtras-text">{res['xtras']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            if st.session_state.serie_sel: st.info("Complete la selección.")
else:
    st.info("Seleccione una Serie.")
