import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(
    page_title="Caudales & Factor Check", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* ELIMINAR SIDEBAR Y AJUSTAR ESPACIO SUPERIOR */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .block-container {
        padding-top: 4rem !important; 
    }

    /* TÍTULO AZUL: GRANDE Y NEGRITA */
    .main-title {
        font-family: sans-serif;
        color: #1E88E5;
        font-size: 55px; /* Tamaño aumentado */
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        line-height: 1.1;
    }
    
    /* FIRMA: PEQUEÑA Y DISCRETA */
    .header-info {
        font-family: sans-serif;
        color: #666;
        font-size: 15px; /* Tamaño disminuido */
        text-align: center;
        margin-bottom: 40px;
        font-style: italic;
        opacity: 0.7;
    }

    /* ESTILOS DE COMPONENTES */
    .w-label { 
        font-family: sans-serif; 
        font-size: 14px; 
        font-weight: bold;
        color: #444;
        margin-bottom: 5px;
        display: block;
    }

    .caudal-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 25px;
        gap: 15px;
    }
    
    .w-caudal {
        background-color: #E8F5E9; color: #2E7D32;
        font-size: 24px; font-weight: bold; text-align: center;
        padding: 5px 30px; border-radius: 12px; border: 2px solid #4CAF50;
    }
    
    .factor-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        max-width: 200px;
        margin: 0 auto;
    }

    .w-factor-header {
        background-color: #E3F2FD; color: #0D47A1;
        font-size: 15px; font-weight: bold; text-align: center;
        padding: 10px; border-radius: 8px 8px 0 0; border: 1px solid #2196F3;
        width: 100%;
    }

    .stImage > img {
        border-left: 1px solid #2196F3;
        border-right: 1px solid #2196F3;
        max-width: 200px !important;
        display: block;
    }

    .w-factor-footer {
        background-color: #F5F5F5; color: #1565C0;
        font-size: 26px; font-weight: bold; text-align: center;
        padding: 10px; border-radius: 0 0 8px 8px; border: 1px solid #2196F3;
        width: 100%;
    }

    .w-xtras-container {
        border: 1px solid #2196F3; padding: 20px; border-radius: 12px;
        background-color: #F1F8E9; margin-top: 35px;
        max-width: 550px; margin-left: auto; margin-right: auto;
    }

    div.stButton > button[kind="primary"] {
        background-color: #1E88E5 !important;
        color: white !important;
        font-weight: bold;
    }
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
if df is None:
    st.error("Archivo Excel no encontrado.")
    st.stop()

# --- CABECERA ---
st.markdown('<p class="main-title">Caudales & Factor Check</p>', unsafe_allow_html=True)
st.markdown('<p class="header-info">🛠️ Soporte Técnico SAT | By C@renasM</p>', unsafe_allow_html=True)

# --- SELECTOR DE SERIE ---
series = sorted(df['serie'].unique())
if "serie_sel" not in st.session_state: st.session_state.serie_sel = None

cols_s = st.columns(len(series))
for i, s in enumerate(series):
    tipo = "primary" if st.session_state.serie_sel == s else "secondary"
    if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True, type=tipo):
        st.session_state.serie_sel = s
        st.rerun()

# --- ÁREA DE TRABAJO ---
if st.session_state.serie_sel:
    df_f = df[df['serie'] == st.session_state.serie_sel]
    col_izq, col_der = st.columns([1, 2.5])

    with col_izq:
        st.markdown('<span class="w-label">Dimensión (mm)</span>', unsafe_allow_html=True)
        sel_dim = st.selectbox("dim", ["- Seleccionar -"] + sorted(df_f['dimension'].unique().tolist()), label_visibility="collapsed")
        
        if sel_dim != "- Seleccionar -":
            df_f = df_f[df_f['dimension'] == sel_dim]
            st.markdown('<span class="w-label">Modelo</span>', unsafe_allow_html=True)
            sel_mod = st.selectbox("mod", ["- Seleccionar -"] + sorted(df_f['modelo'].unique().tolist()), label_visibility="collapsed")
            
            if sel_mod != "- Seleccionar -":
                df_f = df_f[df_f['modelo'] == sel_mod]
                st.markdown('<span class="w-label">Año</span>', unsafe_allow_html=True)
                sel_ano = st.selectbox("ano", ["- Seleccionar -"] + sorted(df_f['año'].unique().tolist()), label_visibility="collapsed")

    with col_der:
        if 'sel_ano' in locals() and sel_ano != "- Seleccionar -" and not df_f.empty:
            res = df_f[df_f['año'] == sel_ano].iloc[0]
            
            # Caudal
            st.markdown(f'<div class="caudal-container"><span style="font-weight: bold; color: #555;">Caudal Consigna</span><div class="w-caudal">{res["consigna"]} m³/h</div></div>', unsafe_allow_html=True)

            # Factores
            f_cols = st.columns(2)
            with f_cols[0]:
                st.markdown('<div class="factor-block">', unsafe_allow_html=True)
                st.markdown('<div class="w-factor-header">Bypass</div>', unsafe_allow_html=True)
                if os.path.exists("fotos/bypass.jpg"): st.image("fotos/bypass.jpg")
                st.markdown(f'<div class="w-factor-footer">{res["factor-bypass"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                    
            with f_cols[1]:
                st.markdown('<div class="factor-block">', unsafe_allow_html=True)
                st.markdown('<div class="w-factor-header">Lower</div>', unsafe_allow_html=True)
                if os.path.exists("fotos/lower.jpg"): st.image("fotos/lower.jpg")
                st.markdown(f'<div class="w-factor-footer">{res["factor-lower"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Xtras
            st.markdown(f'<div class="w-xtras-container"><div style="color: #1E88E5; font-weight: bold; font-size: 16px; text-align: center; margin-bottom: 5px;">Notas Adicionales (Xtras)</div><div style="font-size: 14px; text-align: center; color: #333;">{res["xtras"]}</div></div>', unsafe_allow_html=True)
else:
    st.info("Seleccione una Serie arriba para visualizar los datos.")
