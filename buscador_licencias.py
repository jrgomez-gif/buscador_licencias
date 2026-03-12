import streamlit as st
import pandas as pd
import random
import unicodedata
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS (CSS)
# ==========================================
st.set_page_config(page_title="Padrón Sanitario - COFEPRIS", layout="wide")

# Colores Oficiales Gobierno de México
VERDE_GOB = "#285C4D"  # Verde Institucional
GUINDA_GOB = "#621132" # Guinda Institucional
ORO_GOB = "#D4C19C"    # Oro Institucional

st.markdown(f"""
    <style>
    /* SOLUCIÓN A TU PROBLEMA:
       Estilo del Menú Lateral (Sidebar) con Fondo VERDE
       y Texto FORZADO A BLANCO para legibilidad.
    */
    [data-testid="stSidebar"] {{
        background-color: {VERDE_GOB};
    }}
    
    /* Forzar color de texto BLANCO para todos los elementos
       dentro del sidebar. Targeteamos selectores específicos.
    */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stText,
    [data-testid="stSidebar"] .stMultiSelect div label {{
        color: white !important;
    }}
    
    /* Estilo para los textos de ayuda y subtítulos en el sidebar */
    [data-testid="stSidebar"] .stCaption {{
        color: #e0e0e0 !important;
    }}

    /* Tarjetas de Métricas (Numeralia) */
    .metric-card {{
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-top: 5px solid {GUINDA_GOB};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }}
    .metric-card h3 {{ margin: 0; color: {GUINDA_GOB}; font-size: 1.8rem; }}
    .metric-card p {{ margin: 0; color: #666; font-weight: bold; font-size: 0.8rem; }}

    /* Ficha Técnica Detallada */
    .ficha-tecnica {{
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        border-left: 10px solid {ORO_GOB};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    /* Botones personalizados con color Guinda */
    .stButton>button {{
        background-color: {GUINDA_GOB};
        color: white;
        border-radius: 5px;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNCIONES DE APOYO Y DATOS
# ==========================================
def normalizar_texto(texto):
    """Limpia acentos y estandariza texto para búsquedas precisas."""
    if not isinstance(texto, str): return str(texto)
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.lower()

@st.cache_data
def generar_universo_datos(n=1200):
    """Genera 1,200 registros ficticios con estructura de COFEPRIS."""
    empresas = ["Farmacéutica", "Laboratorios", "Distribuidora Médica", "Logística Sanitaria", "Bioquímicos", "Salud Total"]
    regiones = ["Norte", "Sur", "Bajío", "Occidente", "Centro", "Global", "Nacional"]
    tipos = ["Licencia Sanitaria", "Permiso de Publicidad", "Aviso de Funcionamiento", "Registro Sanitario"]
    estatus_opciones = ["✅ Vigente", "✅ Vigente", "⚠️ Vencida", "⏳ En Proceso"]
    
    data = []
    for i in range(1, n + 1):
        nombre = f"{random.choice(empresas)} {random.choice(regiones)} {random.randint(10, 99)}"
        folio = f"2026-CAS-{str(i).zfill(4)}"
        estatus = random.choice(estatus_opciones)
        vigencia = (datetime.now() + timedelta(days=random.randint(-200, 800))).strftime("%d/%m/%Y")
        
        data.append({
            "Folio": folio,
            "Empresa": nombre,
            "RFC": f"{nombre[:3].upper()}{random.randint(70,99)}0101XYZ",
            "Tipo": random.choice(tipos),
            "Estatus": estatus,
            "Vigencia": vigencia,
            "Responsable": f"Dr(a). {random.choice(['Gomez', 'Rodriguez', 'Perez', 'Hernandez'])}",
            "Ubicación": f"Sede {random.randint(1,32)}"
        })
    return pd.DataFrame(data)

# Cargar datos
df_total = generar_universo_datos()

# --- LÓGICA DE RESETEO (CALLBACK) ---
def reset_filtros():
    """Función para restablecer los filtros a su estado inicial."""
    # Obtenemos los valores por defecto
    tipos_disponibles = sorted(df_total['Tipo'].unique())
    estatus_disponibles = sorted(df_total['Estatus'].unique())
    
    # Actualizamos el session_state
    st.session_state["tipo_filter"] = tipos_disponibles
    st.session_state["estatus_filter"] = estatus_disponibles
    st.session_state["search_input"] = ""

# ==========================================
# 3. SIDEBAR (MENÚ IZQUIERDO)
# ==========================================
with st.sidebar:
    # Usando ruta relativa para GitHub / Streamlit Cloud
    logo_path = "COFEPRIS.png"
    try:
        st.image(logo_path, width=220)
    except:
        st.error("Logo no encontrado.")
    
    st.header("Filtros de Búsqueda")
    
    # Obtenemos los valores por defecto para los multiselects
    tipos_disponibles = sorted(df_total['Tipo'].unique())
    estatus_disponibles = sorted(df_total['Estatus'].unique())

    # Multiselectores con llaves (keys) vinculadas para el reset
    st.multiselect("Tipo de Licencia:", options=tipos_disponibles, 
                   default=tipos_disponibles, key="tipo_filter")
    
    st.multiselect("Estado del Trámite:", options=estatus_disponibles, 
                   default=estatus_disponibles, key="estatus_filter")
    
    st.divider()
    
    # BOTÓN DE RESETEO con callback para evitar errores de API
    st.button("🔄 Restablecer Filtros", on_click=reset_filtros)
    
    st.caption(f"v1.4 | COFEPRIS Data Science")
    st.caption(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

# ==========================================
# 4. CUERPO PRINCIPAL (NUMERALIA Y TABLA)
# ==========================================
st.title("📂 Padrón Federal de Licencias Sanitarias")

# Aplicar filtros basados en el session_state
df_filtrado = df_total[
    df_total['Tipo'].isin(st.session_state["tipo_filter"]) & 
    df_total['Estatus'].isin(st.session_state["estatus_filter"])
]

# Numeralia dinámica
m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f'<div class="metric-card"><h3>{len(df_total)}</h3><p>UNIVERSO TOTAL</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-card"><h3>{len(df_filtrado)}</h3><p>RESULTADOS FILTRO</p></div>', unsafe_allow_html=True)
with m3: 
    vigentes = len(df_filtrado[df_filtrado['Estatus'].str.contains('✅')])
    st.markdown(f'<div class="metric-card"><h3>{vigentes}</h3><p>✅ VIGENTES</p></div>', unsafe_allow_html=True)
with m4:
    vencidas = len(df_filtrado[df_filtrado['Estatus'].str.contains('⚠️')])
    st.markdown(f'<div class="metric-card"><h3>{vencidas}</h3><p>⚠️ VENCIDAS</p></div>', unsafe_allow_html=True)

st.write("")

# BUSCADOR INTELIGENTE con llave vinculada para el reset
busqueda_raw = st.text_input("🔍 Buscar por Empresa, RFC o Folio:", key="search_input", placeholder="Ej: laboratorios...")

if busqueda_raw:
    term = normalizar_texto(busqueda_raw)
    # Buscamos en todas las columnas convirtiendo la fila a un solo string normalizado
    mask = df_filtrado.apply(lambda row: term in normalizar_texto(" ".join(row.astype(str))), axis=1)
    df_filtrado = df_filtrado[mask]

# Tabla de resultados
st.subheader(f"Listado de Registros ({len(df_filtrado)})")
st.dataframe(
    df_filtrado, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Vigencia": st.column_config.TextColumn("Vencimiento"),
        "Empresa": st.column_config.TextColumn("Razón Social", width="large")
    }
)

# ==========================================
# 5. SECCIÓN DE DETALLE (LA FICHA TÉCNICA)
# ==========================================
if not df_filtrado.empty:
    st.divider()
    st.subheader("📝 Inspección Detallada")
    
    # Selector de folio basado en la búsqueda actual
    folio_sel = st.selectbox("Seleccione un folio para ver el expediente:", df_filtrado['Folio'])
    info = df_total[df_total['Folio'] == folio_sel].iloc[0]

    col_info, col_doc = st.columns([1, 1.2])

    with col_info:
        # Ficha Técnica con diseño COFEPRIS
        st.markdown(f"""
            <div class="ficha-tecnica">
                <h2 style='color: {VERDE_GOB}; margin: 0;'>{info['Empresa']}</h2>
                <p style='color: gray; margin-bottom: 20px;'>Folio de Control: {info['Folio']}</p>
                <p><b>🆔 RFC:</b> {info['RFC']}</p>
                <p><b>📋 Trámite:</b> {info['Tipo']}</p>
                <p><b>👨‍🔬 Responsable:</b> {info['Responsable']}</p>
                <p><b>📍 Ubicación:</b> {info['Ubicación']}</p>
                <p><b>📅 Vigencia:</b> {info['Vigencia']}</p>
                <hr>
                <h3 style='color: {"green" if "✅" in info["Estatus"] else "red"};'>
                    {info['Estatus']}
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Como solicitaste, se eliminó el botón de desbloqueo/edición.

    with col_doc:
        # Previsualización del documento
        st.info(f"Visualización de Expediente Digital: {info['Folio']}")
        # Placeholder del PDF. En producción, aquí se incrusta el documento real.
        st.image("https://www.gob.mx/cms/uploads/article/main_image/83942/Licencia.JPG", 
                 caption="Copia Digital Certificada", use_container_width=True)
        # Botón de descarga con el color institucional
        st.download_button("📥 Descargar Archivo PDF", "PDF_DATA", file_name=f"{info['Folio']}.pdf")
else:
    st.warning("No se encontraron registros.")
