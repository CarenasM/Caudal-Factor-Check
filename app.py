import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(page_title="Caudales & Factor Check", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* Título Principal */
    .main-title {
        font-family: sans-serif;
        color: #0D47A1;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .w-label { 
        font-family: sans-serif; 
        font-size: 16px; 
        font-style: italic; 
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
    }
    .stSelectbox { margin-bottom: 15px; }
    
    .caudal-container {
        height: 60px;
        display: flex;
        align-items: center;
    }
    
    .w-caudal {
        background-color: #90EE90; color: #1b5e20;
        font-size: 22px; font-weight: bold; text-align: center;
        padding: 5px 15px; border-radius: 8px; border: 2px solid #2e7d32;
        display: inline-block;
    }
    
    .w-factor-row {
        margin-top: 25px; 
    }
    
    .w-factor {
        background-color: #E3F2FD; color: #0D47A1;
        font-size: 14px; font-weight: bold; text-align: center;
        padding: 8px; border-radius: 8px; border: 1px solid #2196F3;
        min-height: 85px;
    }
    .w-factor-val { font-size: 20px; display: block; margin-top: 2px; }
    
    .w-xtras-container {
        border: 1px solid #333; padding: 10px; border-radius: 5px;
        background-color: #fff; margin-top: 20px;
    }
    .w-xtras-title { color: red; font-style: italic; font-weight: bold; font-size: 14px; text-align: center; margin-bottom: 2px; }
    .w-xtras-text { font-size: 13px; text-align: center; color: #333; }
    
    div.stButton > button[kind="primary"] {
        background-color: #00BFFF !important; 
        color: white !important;
        border: 1px solid #00BFFF !important;
    }
    div.stButton > button { font-size: 14px !important; padding: 2px !important; border: 1px solid #ccc !important; }
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

# Firma en la barra lateral
st.sidebar.markdown("---")
st.sidebar.write("🛠️ **Soporte Técnico SAT**")
st.sidebar.markdown("By **C@renasM**")

# --- CABECERA ---
st.markdown('<p class="main-title">Caudales & Factor Check</p>', unsafe_allow_html=True)
st.write("Seleccione parámetros para acceder a la información")

# --- 1. BOTONES DE SERIE ---
st.markdown('<p class="w-label">Serie</p>', unsafe_allow_html=True)
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
            
            # --- FILA DE CABECERA (Caudal) ---
            st.markdown(f"""
                <div class="caudal-container">
                    <span style="margin-right: 10px; font-weight: bold; font-size: 14px;">Caudal Consigna (m³/h)</span>
                    <div class="w-caudal">{res['consigna']}</div>
                </div>
            """, unsafe_allow_html=True)

            # --- FILA DE FACTORES ---
            st.markdown('<div class="w-factor-row">', unsafe_allow_html=True)
            f_cols = st.columns(2)
            with f_cols[0]:
                st.markdown(f'<div class="w-factor">Factor-Bypass<br><span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
                if os.path.exists("fotos/guia_bypass.jpg"): st.image("fotos/guia_bypass.jpg")
                else: st.caption("📸 Foto Bypass")
                    
            with f_cols[1]:
                st.markdown(f'<div class="w-factor">Factor-Lower<br><span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
                if os.path.exists("fotos/guia_lower.jpg"): st.image("fotos/guia_lower.jpg")
                else: st.caption("📸 Foto Lower")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="w-xtras-container">
                    <div class="w-xtras-title">Xtras</div>
                    <div class="w-xtras-text">{res['xtras']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            if st.session_state.serie_sel: st.info("Complete la selección para ver los resultados.")
else:
    st.info("Por favor, seleccione una Serie para comenzar.")
