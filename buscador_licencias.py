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
    [data-testid="stSidebar"] {{ background-color: {VERDE_GOB}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .metric-card {{
        background-color: white; padding: 15px; border-radius: 8px;
        border-top: 5px solid {GUINDA_GOB}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }}
    .metric-card h3 {{ margin: 0; color: {GUINDA_GOB}; font-size: 1.8rem; }}
    .metric-card p {{ margin: 0; color: #666; font-weight: bold; font-size: 0.8rem; }}
    .ficha-tecnica {{
        background-color: white; padding: 25px; border-radius: 10px;
        border-left: 10px solid {ORO_GOB}; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNCIONES DE APOYO Y DATOS
# ==========================================
def normalizar_texto(texto):
    if not isinstance(texto, str): return str(texto)
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.lower()

@st.cache_data
def generar_universo_datos(n=1200):
    empresas = ["Farmacéutica", "Laboratorios", "Distribuidora Médica PISA", "Logística Sanitaria", "Bioquímicos", "Salud Total"]
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
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Padrón Filtrado')
    return output.getvalue()

def resaltar_vencidas(row):
    if 'Vencida' in str(row['Estatus']):
        return ['background-color: #ffcccc; color: #900000; font-weight: bold;'] * len(row)
    return [''] * len(row)

def limpiar_filtros():
    st.session_state.search_input = ""
    st.session_state.tipo_input = "Todos"
    st.session_state.estatus_input = "Todos"

df_total = generar_universo_datos()

if 'search_input' not in st.session_state: st.session_state.search_input = ""
if 'tipo_input' not in st.session_state: st.session_state.tipo_input = "Todos"
if 'estatus_input' not in st.session_state: st.session_state.estatus_input = "Todos"

opciones_tipo = ["Todos"] + sorted(df_total['Tipo'].unique())
opciones_estatus = ["Todos"] + sorted(df_total['Estatus'].unique())

# ==========================================
# 3. SIDEBAR (CONTEXTO EDUCATIVO)
# ==========================================
with st.sidebar:
    try:
        st.image("COFEPRIS.png", width=220)
    except Exception:
        st.warning("⚠️ Logo 'COFEPRIS.png' no encontrado.")
        
    st.header("📖 Guía de Usuario")
    
    st.markdown("""
    ### ¿Qué es una Licencia Sanitaria?
    Es la autorización oficial expedida por la autoridad sanitaria que permite a un establecimiento operar legalmente, garantizando que cumple con las condiciones de higiene y seguridad para la salud pública.

    ### Significado de los Estatus:
    * **✅ Vigente:** Licencia activa, aprobada y dentro de su periodo de validez legal.
    * **⚠️ Vencida:** El plazo ha expirado. Requiere iniciar trámite de renovación inmediatamente.
    * **⏳ En Proceso:** Trámite ingresado y actualmente bajo evaluación de la autoridad.
    
    ---
    ### 💡 Tip de Búsqueda:
    1. Utiliza los filtros para encontrar el establecimiento.
    2. Identifica el **Folio** en la tabla.
    3. Copia y pega ese número en la sección de **"Inspección Detallada"** (al final de la página) para ver toda la información técnica.
    """)
    st.write("---")
    st.caption("v1.9 BI & Data Engineering COFEPRIS 2026")

# ==========================================
# 4. CUERPO PRINCIPAL (RESUMEN SUPERIOR)
# ==========================================
st.title("📂 Padrón Federal de Licencias Sanitarias")
resumen_superior = st.container()
st.divider()

# ==========================================
# 5. TABLA, FILTROS Y DESCARGAS
# ==========================================
col_f1, col_f2, col_f3 = st.columns([2, 1.5, 1.5])
with col_f1:
    busqueda_texto = st.text_input("🔍 Búsqueda por palabra clave:", key="search_input", placeholder="Ej. PISA, Farmacéutica, Folio...")
with col_f2:
    tipo_sel = st.selectbox("Filtrar por Tipo de Trámite:", options=opciones_tipo, key="tipo_input")
with col_f3:
    estatus_sel = st.selectbox("Filtrar por Estatus:", options=opciones_estatus, key="estatus_input")

df_filtrado = df_total.copy()

if tipo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_sel]
if estatus_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Estatus'] == estatus_sel]

if busqueda_texto:
    term = normalizar_texto(busqueda_texto)
    mask = df_filtrado.apply(lambda row: term in normalizar_texto(" ".join(row.astype(str))), axis=1)
    df_filtrado = df_filtrado[mask]

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

st.info(f"🔎 **Se encontraron {len(df_filtrado)} licencias** aplicando los filtros actuales.")

col_tabla_header, col_reset, col_descarga = st.columns([2.5, 1, 1])
with col_tabla_header:
    st.subheader("📋 Listado de Registros")
with col_reset:
    st.write("") 
    st.button("🔄 Limpiar Filtros", on_click=limpiar_filtros, use_container_width=True)
with col_descarga:
    if not df_filtrado.empty:
        excel_data = to_excel(df_filtrado)
        st.write("") 
        st.download_button(
            label="📥 Descargar en Excel", data=excel_data,
            file_name=f"Padron_Licencias_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

if not df_filtrado.empty:
    df_estilizado = df_filtrado.style.apply(resaltar_vencidas, axis=1)
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True, height=350)
else:
    st.warning("No hay registros que coincidan con la selección.")

# ==========================================
# 6. FICHA TÉCNICA (NUEVO BUSCADOR DE TEXTO LIBRE)
# ==========================================
st.write("---")
st.subheader("📝 Inspección Detallada del Expediente")

# Cambiamos selectbox por text_input para facilitar el Copiar/Pegar
folio_busqueda = st.text_input("🔎 Pegue o escriba el Folio a inspeccionar (Ej. 2026-CAS-0001):", key="folio_ficha")

if folio_busqueda:
    term_folio = normalizar_texto(folio_busqueda).strip()
    # Buscamos en el total de datos (por si el usuario busca un folio que no está en los filtros actuales)
    mask_ficha = df_total['Folio'].apply(lambda f: term_folio in normalizar_texto(str(f)))
    coincidencias = df_total[mask_ficha]
    
    if not coincidencias.empty:
        info = coincidencias.iloc[0] # Mostramos el primer resultado coincidente
        
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
                <h3 style='color: {"green" if "✅" in info["Estatus"] else "orange" if "⏳" in info["Estatus"] else "#900000"};'>
                    Estado actual: {info['Estatus']}
                </h3>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ No se encontró ningún expediente asociado al folio o término: '{folio_busqueda}'.")
else:
    st.info("👆 Copie un Folio de la tabla superior y péguelo en el recuadro de arriba para visualizar su ficha técnica completa.")
