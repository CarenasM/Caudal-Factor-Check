import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
EXCEL_FILE = "datos_caudales.xlsx"

st.set_page_config(page_title="Configurador Waldner - Interfaz Fiel", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS ---
# Aquí imitamos los colores y bordes de tu Excel
st.markdown("""
    <style>
    /* Estilo para los textos de cabecera (Serie, Dimensión...) */
    .w-label {
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-style: italic;
        margin-bottom: -5px;
    }
    
    /* Cuadro de Caudal (Verde claro con borde) */
    .w-caudal {
        background-color: #90EE90; /* LightGreen */
        color: #2e7d32; /* Texto verde oscuro */
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #2e7d32;
        margin-bottom: 20px;
    }
    
    /* Cuadros de Factores (Azul claro con borde) */
    .w-factor {
        background-color: #E3F2FD; /* Azul muy claro */
        color: #1976D2; /* Texto azul oscuro */
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #2196F3;
    }
    .w-factor-val {
        font-size: 28px;
        display: block;
        margin-top: 5px;
    }
    
    /* Cuadro de Xtras (Blanco con borde negro y título rojo) */
    .w-xtras-container {
        border: 1px solid black;
        padding: 15px;
        border-radius: 5px;
        margin-top: 20px;
        background-color: white;
    }
    .w-xtras-title {
        color: red;
        font-style: italic;
        font-weight: bold;
        font-size: 18px;
        text-align: center;
        margin-bottom: 5px;
    }
    .w-xtras-text {
        font-size: 16px;
        text-align: center;
    }
    
    /* Estilo para los botones de Serie con colores dinámicos */
    div.stButton > button:first-child {
        font-size: 18px;
        border-radius: 5px;
        padding: 10px 15px;
        border: 1px solid black;
    }
    
    /* Definición de colores para los botones (Aproximación de tu Excel) */
    .st-btn-w90 { background-color: #E6B89C !important; color: black !important; } /* Naranja suave */
    .st-btn-mc6 { background-color: #E6E6E6 !important; color: black !important; } /* Gris muy claro */
    .st-btn-scala { background-color: #737373 !important; color: white !important; } /* Gris oscuro */
    .st-btn-si3 { background-color: #DDE2EC !important; color: black !important; } /* Gris azulado */
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    if not os.path.exists(EXCEL_FILE):
        return None
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Limpieza de cabeceras
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Limpieza de datos (Evitar error applymap de Pandas)
        df = df.fillna("N/A").astype(str)
        if hasattr(df, 'map'):
            df = df.map(lambda x: x.strip())
        else:
            df = df.applymap(lambda x: x.strip())
        return df
    except Exception as e:
        st.error(f"Error al cargar Excel: {e}")
        return None

df = cargar_datos()

if df is None:
    st.error(f"⚠️ No se encontró el archivo {EXCEL_FILE} en el repositorio.")
    st.stop()

# --- INTERFAZ GRAFICA ---
st.write("Seleccione ó pulse en los botones de cada recuadro para acceder a la información")

# --- 1. SELECCIÓN DE SERIE (BOTONES) ---
st.markdown('<p class="w-label">Serie</p>', unsafe_allow_html=True)
series_disponibles = sorted(df['serie'].unique())

if "serie_sel" not in st.session_state:
    # Intenta poner SCALA por defecto (como en tu foto)
    st.session_state.serie_sel = "SCALA" if "SCALA" in series_disponibles else series_disponibles[0]

cols_s = st.columns(4) # Ajustado a tus 4 series

for i, s in enumerate(series_disponibles):
    if i >= 4: break # Limitamos a 4 columnas por si acaso
    
    # Asignamos color dinámico según la serie
    cls_btn = f"st-btn-{s.lower()}"
    
    # Renderizamos el botón
    if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True, help=f"Elegir Serie {s}"):
        st.session_state.serie_sel = s
        st.rerun()

    # Pequeño truco CSS para aplicar el color al botón específico
    st.markdown(f'<style>button[key="btn_{s}"] {{ background-color: var(--{cls_btn}-bg) !important; color: var(--{cls_btn}-text) !important; }}</style>', unsafe_allow_html=True)

# Definimos las variables CSS para los colores
st.markdown("""
    <style>
    :root {
        --st-btn-w90-bg: #E6B89C; --st-btn-w90-text: black;
        --st-btn-mc6-bg: #E6E6E6; --st-btn-mc6-text: black;
        --st-btn-scala-bg: #737373; --st-btn-scala-text: white;
        --st-btn-si3-bg: #DDE2EC; --st-btn-si3-text: black;
    }
    </style>
""", unsafe_allow_html=True)


st.write("") # Espacio

# --- 2. FILTROS Y RESULTADOS EN COLUMNAS ---
# Dividimos la pantalla en Izquierda (filtros) y Derecha (imágenes y resultados)
col_izq, col_der = st.columns([1, 1.5])

with col_izq:
    # Lógica de cascada sobre la serie elegida
    df_f = df[df['serie'] == st.session_state.serie_sel]
    
    # FILTRO DIMENSIÓN
    st.markdown('<p class="w-label">Dimensión</p>', unsafe_allow_html=True)
    dim_opts = sorted(df_f['dimension'].unique(), key=lambda x: int(x) if x.isdigit() else 0)
    sel_dim = st.selectbox("", dim_opts, label_visibility="collapsed")
    st.markdown('<p style="font-size:16px; margin-top:-10px;">mm</p>', unsafe_allow_html=True)
    df_f = df_f[df_f['dimension'] == sel_dim]
    
    # FILTRO MODELO
    st.markdown('<p class="w-label">Modelo</p>', unsafe_allow_html=True)
    mod_opts = sorted(df_f['modelo'].unique())
    sel_mod = st.selectbox("", mod_opts, label_visibility="collapsed")
    df_f = df_f[df_f['modelo'] == sel_mod]
    
    # FILTRO AÑO
    st.markdown('<p class="w-label">Año</p>', unsafe_allow_html=True)
    ano_opts = df_f['año'].unique()
    sel_ano = st.selectbox("", ano_opts, label_visibility="collapsed")
    df_f = df_f[df_f['año'] == sel_ano]

with col_der:
    if not df_f.empty:
        res = df_f.iloc[0] # Cogemos la primera coincidencia
        
        # FILA 1 DE RESULTADOS: Caudal
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center;">
                <p style="margin-right: 15px; font-weight: bold; font-size: 18px;">Caudal Consigna (m³/h)</p>
                <div class="w-caudal">{res['consigna']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Espacio
        
        # FILA 2 DE RESULTADOS: Factores y Fotos
        # Creamos dos columnas más estrechas para Factor-Bypass y Factor-Lower
        f1, f2 = st.columns(2)
        
        with f1:
            # Título y Valor Factor Bypass
            st.markdown(f'<div class="w-factor">Factor-Bypass<br><span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
            
            # Foto 1 (Bypass)
            img1_path = "fotos/guia_bypass.jpg" # O como la hayas llamado
            if os.path.exists(img1_path):
                st.image(img1_path, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x200.png?text=Foto+Bypass", caption="Sin foto")
                
        with f2:
            # Título y Valor Factor Lower
            st.markdown(f'<div class="w-factor">Factor-Lower<br><span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
            
            # Foto 2 (Lower)
            img2_path = "fotos/guia_lower.jpg" # O como la hayas llamado
            if os.path.exists(img2_path):
                st.image(img2_path, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x200.png?text=Foto+Lower", caption="Sin foto")
        
        st.divider() # Línea de separación antes de Xtras
        
        # FILA 3 DE RESULTADOS: Xtras
        st.markdown(f"""
            <div class="w-xtras-container">
                <div class="w-xtras-title">Xtras</div>
                <div class="w-xtras-text">{res['xtras']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        # En caso de no encontrar datos, mostramos el estado "vacío" de tu imagen
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center;">
                <p style="margin-right: 15px; font-weight: bold; font-size: 18px;">Caudal Consigna (m³/h)</p>
                <div class="w-caudal" style="background-color:#ffebee; color:#b71c1c; border-color:#b71c1c;">No encontrado</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning("No se han encontrado datos para esta combinación.")

if st.sidebar.button("Cerrar / Logout"):
    # (Aquí iría la lógica de login si lo quieres añadir)
    st.session_state.serie_sel = series_disponibles[0]
    st.rerun()