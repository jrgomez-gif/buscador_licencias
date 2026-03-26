import streamlit as st
import pandas as pd
import random
import unicodedata
import io
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS (CSS)
# ==========================================
st.set_page_config(page_title="Padrón Sanitario - COFEPRIS", layout="wide")

VERDE_GOB = "#285C4D"
GUINDA_GOB = "#621132"
ORO_GOB = "#D4C19C"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background-color: {VERDE_GOB};
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
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
    .ficha-tecnica {{
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        border-left: 10px solid {ORO_GOB};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNCIONES DE APOYO Y DATOS
# ==========================================
@st.cache_data
def generar_universo_datos(n=1200):
    empresas = ["Farmacéutica", "Laboratorios", "Distribuidora Médica", "Logística Sanitaria", "Bioquímicos", "Salud Total"]
    regiones = ["Norte", "Sur", "Bajío", "Occidente", "Centro", "Global", "Nacional"]
    tipos = ["Licencia Sanitaria", "Permiso de Publicidad", "Aviso de Funcionamiento", "Registro Sanitario"]
    estatus_opciones = ["✅ Vigente", "✅ Vigente", "⚠️ Vencida", "⏳ En Proceso"]
    
    data = []
    for i in range(1, n + 1):
        nombre = f"{random.choice(empresas)} {random.choice(regiones)} {random.randint(10, 99)}"
        folio = f"2026-CAS-{str(i).zfill(4)}"
        data.append({
            "Folio": folio,
            "Empresa": nombre,
            "RFC": f"{nombre[:3].upper()}{random.randint(70,99)}0101XYZ",
            "Tipo": random.choice(tipos),
            "Estatus": random.choice(estatus_opciones),
            "Vigencia": (datetime.now() + timedelta(days=random.randint(-200, 800))).strftime("%d/%m/%Y"),
            "Responsable": f"Dr(a). {random.choice(['Gomez', 'Rodriguez', 'Perez', 'Hernandez'])}",
            "Ubicación": f"Sede {random.randint(1,32)}"
        })
    return pd.DataFrame(data)

def to_excel(df):
    """Convierte un DataFrame a un archivo Excel en memoria."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Padrón Filtrado')
    return output.getvalue()

def resaltar_vencidas(row):
    """Aplica color de fondo rojo claro a las filas con estatus Vencida."""
    if 'Vencida' in str(row['Estatus']):
        # Fondo rojo claro y texto rojo oscuro para contraste
        return ['background-color: #ffcccc; color: #900000; font-weight: bold;'] * len(row)
    return [''] * len(row)

df_total = generar_universo_datos()
tipos_disponibles = sorted(df_total['Tipo'].unique())
estatus_disponibles = sorted(df_total['Estatus'].unique())

# ==========================================
# 3. SIDEBAR (MENÚ IZQUIERDO INFORMATIVO)
# ==========================================
with st.sidebar:
    st.image("https://www.gob.mx/cms/uploads/image/file/489433/COFEPRIS_2018.png", width=220)
    st.header("📖 Guía de Estatus")
    
    st.markdown("""
    Significado de los estatus de las licencias:
    
    * **✅ Vigente:** Licencia activa, aprobada y dentro de su periodo de validez legal.
    * **⚠️ Vencida:** El plazo de validez ha expirado. Requiere trámite de renovación inmediatamente.
    * **⏳ En Proceso:** Trámite ingresado y actualmente bajo evaluación por la autoridad sanitaria.
    """)
    st.caption(f"v1.8 | BI & Data Engineering")

# ==========================================
# 4. CUERPO PRINCIPAL (RESUMEN SUPERIOR)
# ==========================================
st.title("📂 Padrón Federal de Licencias Sanitarias")

# Reservamos este espacio visual en la parte superior para que se llene después
resumen_superior = st.container()

st.divider()

# ==========================================
# 5. TABLA, FILTROS Y DESCARGA
# ==========================================
col_tabla_header, col_descarga = st.columns([3, 1])
with col_tabla_header:
    st.subheader("📋 Listado de Registros")

# Filtros directamente sobre la tabla
col_f1, col_f2 = st.columns(2)
with col_f1:
    tipo_sel = st.multiselect("Filtrar por Tipo de Trámite:", options=tipos_disponibles, default=tipos_disponibles)
with col_f2:
    estatus_sel = st.multiselect("Filtrar por Estatus:", options=estatus_disponibles, default=estatus_disponibles)

# Filtrar los datos con lo seleccionado
df_filtrado = df_total[
    (df_total['Tipo'].isin(tipo_sel)) & 
    (df_total['Estatus'].isin(estatus_sel))
]

# AHORA SÍ: Llenamos el contenedor superior del resumen con los datos filtrados
with resumen_superior:
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><h3>{len(df_total)}</h3><p>UNIVERSO TOTAL</p></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><h3>{len(df_filtrado)}</h3><p>RESULTADOS EN TABLA</p></div>', unsafe_allow_html=True)
    with m3: 
        vigentes = len(df_filtrado[df_filtrado['Estatus'].str.contains('✅')])
        st.markdown(f'<div class="metric-card"><h3>{vigentes}</h3><p>✅ VIGENTES</p></div>', unsafe_allow_html=True)
    with m4:
        vencidas = len(df_filtrado[df_filtrado['Estatus'].str.contains('⚠️')])
        st.markdown(f'<div class="metric-card"><h3>{vencidas}</h3><p>⚠️ VENCIDAS</p></div>', unsafe_allow_html=True)

# Botón de Descarga
with col_descarga:
    if not df_filtrado.empty:
        excel_data = to_excel(df_filtrado)
        st.write("") # Espaciador para alinear con el título
        st.download_button(
            label="📥 Descargar en Excel",
            data=excel_data,
            file_name=f"Padron_Licencias_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# Renderizar la tabla con colores condicionales (Estilo)
if not df_filtrado.empty:
    # Aplicar la función de coloreado usando Pandas Styler
    df_estilizado = df_filtrado.style.apply(resaltar_vencidas, axis=1)
    
    st.dataframe(
        df_estilizado, 
        use_container_width=True, 
        hide_index=True,
        height=350
    )
else:
    st.warning("No hay registros que coincidan con la selección.")

# ==========================================
# 6. FICHA TÉCNICA
# ==========================================
if not df_filtrado.empty:
    st.write("---")
    st.subheader("📝 Inspección Detallada del Expediente")
    
    folio_sel = st.selectbox("Seleccione un folio específico de la tabla superior:", df_filtrado['Folio'])
    info = df_total[df_total['Folio'] == folio_sel].iloc[0]

    st.markdown(f"""
        <div class="ficha-tecnica">
            <h2 style='color: {VERDE_GOB}; margin: 0;'>{info['Empresa']}</h2>
            <p style='color: gray; margin-bottom: 20px;'>Folio: {info['Folio']}</p>
            <p><b>🆔 RFC:</b> {info['RFC']}</p>
            <p><b>📋 Trámite:</b> {info['Tipo']}</p>
            <p><b>👨‍🔬 Responsable:</b> {info['Responsable']}</p>
            <p><b>📍 Ubicación:</b> {info['Ubicación']}</p>
            <p><b>📅 Vigencia:</b> {info['Vigencia']}</p>
            <hr>
            <h3 style='color: {"green" if "✅" in info["Estatus"] else "orange" if "⏳" in info["Estatus"] else "#900000"};'>
                Estado actual: {info['Estatus']}
            </h3>
        </div>
    """, unsafe_allow_html=True)
