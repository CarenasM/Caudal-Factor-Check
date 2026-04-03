import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(
    page_title="Caudales & Factor Check", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS CORREGIDOS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none; }
    .block-container { padding-top: 2rem !important; }

    /* TÍTULO Y FIRMA */
    .main-title {
        font-family: sans-serif;
        color: #1E88E5;
        font-size: 70px; 
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
    }
    .header-info {
        font-family: sans-serif;
        color: #888;
        font-size: 9px; 
        text-align: center;
        margin-bottom: 40px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ALINEACIÓN DE BLOQUES DE FACTOR */
    .factor-container {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .w-factor-header {
        background-color: #E3F2FD; color: #0D47A1;
        font-size: 16px; font-weight: bold; text-align: center;
        padding: 10px; border-radius: 8px 8px 0 0; border: 1px solid #2196F3;
    }

    .stImage > img {
        border-left: 1px solid #2196F3;
        border-right: 1px solid #2196F3;
        width: 100% !important;
    }

    .w-factor-footer {
        background-color: #F5F5F5; color: #1565C0;
        font-size: 26px; font-weight: bold; text-align: center;
        padding: 12px; border-radius: 0 0 8px 8px; border: 1px solid #2196F3;
    }

    /* REPARACIÓN DE COLORES DE SELECTORES (QUITAR ROJO) */
    .stSelectbox div[data-baseweb="select"] {
        border-color: #d3d3d3 !important;
    }

    .w-label { font-family: sans-serif; font-size: 14px; font-weight: bold; color: #444; margin-bottom: 5px; display: block; }
    .caudal-container { display: flex; justify-content: center; align-items: center; margin-bottom: 25px; gap: 15px; }
    .w-caudal { background-color: #E8F5E9; color: #2E7D32; font-size: 24px; font-weight: bold; padding: 5px 30px; border-radius: 12px; border: 2px solid #4CAF50; }
    .w-xtras-container { border: 1px solid #2196F3; padding: 20px; border-radius: 12px; background-color: #F1F8E9; margin-top: 35px; max-width: 600px; margin-left: auto; margin-right: auto; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
@st.cache_data
def cargar_datos():
    if not os.path.exists(EXCEL_FILE): return None
    try:
        df = pd.read_excel(EXCEL_FILE)
        df.columns = [str(c).strip().lower() for c in df.columns]
        df = df.fillna("N/A").astype(str)
        return df
    except: return None

df = cargar_datos()

# --- CABECERA ---
st.markdown('<p class="main-title">Caudales & Factor Check</p>', unsafe_allow_html=True)
st.markdown('<p class="header-info">SOPORTE TÉCNICO SAT | BY C@RENASM</p>', unsafe_allow_html=True)

if df is not None:
    # Selector de Serie
    series = sorted(df['serie'].unique())
    if "serie_sel" not in st.session_state: st.session_state.serie_sel = None

    cols_s = st.columns(len(series))
    for i, s in enumerate(series):
        tipo = "primary" if st.session_state.serie_sel == s else "secondary"
        if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True, type=tipo):
            st.session_state.serie_sel = s
            st.rerun()

    if st.session_state.serie_sel:
        df_f = df[df['serie'] == st.session_state.serie_sel]
        col_izq, col_der = st.columns([1, 2.5])

        with col_izq:
            st.markdown('<span class="w-label">Dimensión (mm)</span>', unsafe_allow_html=True)
            sel_dim = st.selectbox("dim", ["-"] + sorted(df_f['dimension'].unique().tolist()), label_visibility="collapsed")
            if sel_dim != "-":
                df_f = df_f[df_f['dimension'] == sel_dim]
                st.markdown('<span class="w-label">Modelo</span>', unsafe_allow_html=True)
                sel_mod = st.selectbox("mod", ["-"] + sorted(df_f['modelo'].unique().tolist()), label_visibility="collapsed")
                if sel_mod != "-":
                    df_f = df_f[df_f['modelo'] == sel_mod]
                    st.markdown('<span class="w-label">Año</span>', unsafe_allow_html=True)
                    sel_ano = st.selectbox("ano", ["-"] + sorted(df_f['año'].unique().tolist()), label_visibility="collapsed")

        with col_der:
            if 'sel_ano' in locals() and sel_ano != "-" and not df_f.empty:
                res = df_f[df_f['año'] == sel_ano].iloc[0]
                st.markdown(f'<div class="caudal-container"><span style="font-weight: bold;">Caudal Consigna</span><div class="w-caudal">{res["consigna"]} m³/h</div></div>', unsafe_allow_html=True)

                f_cols = st.columns(2)
                for idx, tipo_f in enumerate(["bypass", "lower"]):
                    with f_cols[idx]:
                        st.markdown(f'<div class="factor-container"><div class="w-factor-header">{tipo_f.capitalize()}</div>', unsafe_allow_html=True)
                        if os.path.exists(f"fotos/{tipo_f}.jpg"):
                            st.image(f"fotos/{tipo_f}.jpg", use_container_width=True)
                        st.markdown(f'<div class="w-factor-footer">{res[f"factor-{tipo_f}"]}</div></div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="w-xtras-container"><div style="color: #1E88E5; font-weight: bold; text-align: center;">Notas Adicionales (Xtras)</div><div style="text-align: center;">{res["xtras"]}</div></div>', unsafe_allow_html=True)

# --- RECARGA ---
st.write("---")
if st.button("🔄 Actualizar Datos del Excel"):
    st.cache_data.clear()
    st.rerun()
