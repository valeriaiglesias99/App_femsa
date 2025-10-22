import streamlit as st
from data_prep import load_data
import pandas as pd
from datetime import date, timedelta

# Páginas
from paginas.dashboard import mostrar_dashboard
from paginas.lona import mostrar_nueva_pagina as mostrar_lona
from paginas.banner_rack import mostrar_nueva_pagina as mostrar_banner
from paginas.incidencia import mostrar_incidencia

# ---------------------
# Cargar datos
# ---------------------
df_final = load_data()

# ---------------------
# Logo de la pagina
# ---------------------

st.set_page_config(
    page_title="Dashboard FEMSA",          # Título que aparece en la pestaña
    page_icon="imagenes/lucro-inside.png" # Ruta a tu logo
)

# ---------------------
# Menú lateral
# ---------------------


with st.sidebar:
    st.image("imagenes/logo FEMSA-05.png", use_container_width=False)


pagina = st.sidebar.selectbox(
    "Selecciona una página",
    ["Lona", "Banner + Rack", "Incidencias"],
    index=0
)

page_bg = """
    <style>
        /* Fondo y texto general */
        body, [data-testid="stAppViewContainer"] {
            background-color: #dddddd;  
            color: black;               
        }

        /* Texto */
        .stText, .stMarkdown {
            color: black;
        }

        /* Contenedor principal */
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0rem !important;   /* elimina el espacio superior */
            max-width: 100% !important;
        }

        /* 🔹 Oculta o minimiza el header de Streamlit */
        [data-testid="stHeader"] {
            height: 0rem;
            background: none;
        }
    </style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------
# Filtros
# ---------------------
df_filtrado = df_final.copy()
df_filtrado["FechaHora_Menos6h"] = pd.to_datetime(df_filtrado["FechaHora_Menos6h_visit"])

# ---------------------
# Logos en la barra lateral
# ---------------------

# Obtener los periodos únicos
periodos = sorted(df_filtrado["Periodo_visit"].dropna().unique())

# --- Filtro con valor predeterminado ---
periodo = st.sidebar.multiselect(
    "Periodo",
    options=periodos,
    default=["Periodo 5"] if "Periodo 5" in periodos else []  # 👈 Predeterminado
)

# --- Aplicar filtro de periodo antes de definir fechas ---
if periodo:
    df_filtrado = df_filtrado[df_filtrado["Periodo_visit"].isin(periodo)]

# --- Ahora, generar rango de fechas según el periodo seleccionado ---
if not df_filtrado.empty:
    min_fecha = df_filtrado["FechaHora_Menos6h"].dt.date.min()
    max_fecha = df_filtrado["FechaHora_Menos6h"].dt.date.max()
else:
    min_fecha = None
    max_fecha = None

# --- Filtros de fecha dinámicos según el periodo seleccionado ---
fecha_inicio = st.sidebar.date_input("Fecha inicio", value=min_fecha)
fecha_fin = st.sidebar.date_input("Fecha fin", value=max_fecha)

tipo_actividad = st.sidebar.multiselect("Tipo de actividad", df_filtrado["name_type"].dropna().unique())
zona = st.sidebar.multiselect("Zona", df_filtrado["store_zone_store"].dropna().unique())
region = st.sidebar.multiselect("Región", df_filtrado["store_region_store"].dropna().unique())
proveedor = st.sidebar.multiselect("Proveedor", df_filtrado["name_provider"].dropna().unique())
pdv_id = st.sidebar.multiselect("PDV", df_filtrado["store_name_store"].dropna().unique())
pdv_sap = st.sidebar.multiselect("SAP", df_filtrado["store_sap_store"].dropna().unique())
tamano = st.sidebar.multiselect("Tamaño", df_filtrado["TamañoAsignado_answer"].dropna().unique())
usuario = st.sidebar.multiselect("Usuario", df_filtrado["full_name_user_provider"].dropna().unique())

with st.sidebar:

    st.image("imagenes/Logo lucro-05.png", use_container_width=False)

# ---------------------
# Aplicar filtros
# ---------------------
if proveedor:
    df_filtrado = df_filtrado[df_filtrado["name_provider"].isin(proveedor)]
if fecha_inicio and fecha_fin:
    df_filtrado = df_filtrado[
        (df_filtrado["FechaHora_Menos6h"].dt.date >= fecha_inicio) &
        (df_filtrado["FechaHora_Menos6h"].dt.date <= fecha_fin)
    ]
if region:
    df_filtrado = df_filtrado[df_filtrado["store_region_store"].isin(region)]
if periodo:
    df_filtrado = df_filtrado[df_filtrado["Periodo_visit"].isin(periodo)]
if tipo_actividad:
    df_filtrado = df_filtrado[df_filtrado["name_type"].isin(tipo_actividad)]
if zona:
    df_filtrado = df_filtrado[df_filtrado["store_zone_store"].isin(zona)]
if pdv_id:
    df_filtrado = df_filtrado[df_filtrado["store_name_store"].isin(pdv_id)]
if pdv_sap:
    df_filtrado = df_filtrado[df_filtrado["store_sap_store"].isin(pdv_sap)]
if usuario:
    df_filtrado = df_filtrado[df_filtrado["full_name_user_provider"].isin(usuario)]
if tamano:
    df_filtrado = df_filtrado[df_filtrado["TamañoAsignado_answer"].isin(tamano)]

# ---------------------
# Navegación entre páginas
# ---------------------
if pagina == "Lona":
    mostrar_lona(df_filtrado)

elif pagina == "Banner + Rack":
    mostrar_banner(df_filtrado)

elif pagina == "Incidencias":
    mostrar_incidencia(df_filtrado)




