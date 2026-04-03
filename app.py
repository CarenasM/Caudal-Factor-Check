import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(page_title="Configurador Waldner SAT", layout="wide")

# --- ESTILOS CSS COMPACTOS ---
st.markdown("""
    <style>
    /* Estilo general y etiquetas */
    .w-label { font-family: sans-serif; font-size: 16px; font-style: italic; margin-bottom: -15px; font-weight: bold; }
    
    /* Cuadro de Caudal compacto */
    .w-caudal {
        background-color: #90EE90; color: #1b5e20;
        font-size: 22px; font-weight: bold; text-align: center;
        padding: 5px 15px; border-radius: 8px; border: 2px solid #2e7d32;
    }
    
    /* Cuadros de Factores compactos */
    .w-factor {
        background-color: #E3F2FD; color: #0D47A1;
        font-size: 14px; font-weight: bold; text-align: center;
        padding: 8px; border-radius: 8px; border: 1px solid #2196F3;
    }
    .w-factor-val { font-size: 20px; display: block; margin-top: 2px; }
    
    /* Cuadro de Xtras compacto */
    .w-xtras-container {
        border: 1px solid #333; padding: 10px; border-radius: 5px;
        background-color: #fff; margin-top: 10px;
    }
    .w-xtras-title { color: red; font-style: italic; font-weight: bold; font-size: 14px; text-align: center; margin-bottom: 2px; }
    .w-xtras-text { font-size: 13px; text-align: center; color: #333; }

    /* Botones de Serie: Azul cuando se selecciona */
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
if df is None:
    st.error("Archivo no encontrado o error en Excel."); st.stop()

st.write("Seleccione parámetros para acceder a la información")

# --- 1. BOTONES DE SERIE (Azul al seleccionar) ---
st.markdown('<p class="w-label">Serie</p>', unsafe_allow_html=True)
series_disponibles = sorted(df['serie'].unique())

if "serie_sel" not in st.session_state:
    st.session_state.serie_sel = series_disponibles[0]

cols_s = st.columns(len(series_disponibles))
for i, s in enumerate(series_disponibles):
    # type="primary" hace que el botón sea Azul en el tema por defecto de Streamlit
    es_activo = "primary" if st.session_state.serie_sel == s else "secondary"
    if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True, type=es_activo):
        st.session_state.serie_sel = s
        st.rerun()

# --- 2. FILTROS Y RESULTADOS ---
col_izq, col_der = st.columns([1, 2])

with col_izq:
    df_f = df[df['serie'] == st.session_state.serie_sel]
    
    st.markdown('<p class="w-label">Dimensión</p>', unsafe_allow_html=True)
    dim_opts = sorted(df_f['dimension'].unique(), key=lambda x: int(x) if str(x).isdigit() else 0)
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
        
        # Caudal arriba a la derecha
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom:10px;">
                <span style="margin-right: 10px; font-weight: bold; font-size: 15px;">Caudal Consigna (m³/h)</span>
                <div class="w-caudal">{res['consigna']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Factores y Fotos
        f_cols = st.columns(2)
        with f_cols[0]:
            st.markdown(f'<div class="w-factor">Factor-Bypass<br><span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
            if os.path.exists("fotos/guia_bypass.jpg"): st.image("fotos/guia_bypass.jpg")
            else: st.caption("📸 Foto Bypass")
                
        with f_cols[1]:
            st.markdown(f'<div class="w-factor">Factor-Lower<br><span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
            if os.path.exists("fotos/guia_lower.jpg"): st.image("fotos/guia_lower.jpg")
            else: st.caption("📸 Foto Lower")
        
        # Xtras abajo
        st.markdown(f"""
            <div class="w-xtras-container">
                <div class="w-xtras-title">Xtras</div>
                <div class="w-xtras-text">{res['xtras']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Sin datos para esta combinación.")
