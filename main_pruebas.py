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
# Menú lateral
# ---------------------
pagina = st.sidebar.selectbox(
    "Selecciona una página",
    ["Ejecución", "Lona", "Banner + Rack", "Incidencias"],
    index=0
)

# ---------------------
# Estilos básicos
# ---------------------
page_bg = """
    <style>
        body, [data-testid="stAppViewContainer"] {
            background-color: #dddddd;  
            color: black;               
        }
        .stText, .stMarkdown {
            color: black;
        }
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100% !important;
        }
    </style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.success("Modo pruebas activado (sin login).")

# ---------------------
# Filtros
# ---------------------
df_filtrado = df_final.copy()
df_filtrado["FechaHora_Menos6h"] = pd.to_datetime(df_filtrado["FechaHora_Menos6h_visit"])

fecha_inicio = st.sidebar.date_input("Fecha inicio")
fecha_fin = st.sidebar.date_input("Fecha fin")

region = st.sidebar.multiselect("Región", df_filtrado["store_region_store"].dropna().unique())
proveedor = st.sidebar.multiselect("Proveedor", df_filtrado["name_provider"].dropna().unique())
periodo = st.sidebar.multiselect("Periodo", df_filtrado["Periodo_visit"].dropna().unique())
tipo_actividad = st.sidebar.multiselect("Tipo de actividad", df_filtrado["name_type"].dropna().unique())
zona = st.sidebar.multiselect("Zona", df_filtrado["store_zone_store"].dropna().unique())
pdv_id = st.sidebar.multiselect("PDV", df_filtrado["store_name_store"].dropna().unique())
usuario = st.sidebar.multiselect("Usuario", df_filtrado["full_name_user_provider"].dropna().unique())
tamano = st.sidebar.multiselect("Tamaño", df_filtrado["TamañoAsignado_answer"].dropna().unique())

# ---------------------
# Aplicar filtros
# ---------------------
if fecha_inicio and fecha_fin:
    df_filtrado = df_filtrado[
        (df_filtrado["FechaHora_Menos6h"].dt.date >= fecha_inicio) &
        (df_filtrado["FechaHora_Menos6h"].dt.date <= fecha_fin)
    ]

if region:
    df_filtrado = df_filtrado[df_filtrado["store_region_store"].isin(region)]
if proveedor:
    df_filtrado = df_filtrado[df_filtrado["name_provider"].isin(proveedor)]
if periodo:
    df_filtrado = df_filtrado[df_filtrado["Periodo_visit"].isin(periodo)]
if tipo_actividad:
    df_filtrado = df_filtrado[df_filtrado["name_type"].isin(tipo_actividad)]
if zona:
    df_filtrado = df_filtrado[df_filtrado["store_zone_store"].isin(zona)]
if pdv_id:
    df_filtrado = df_filtrado[df_filtrado["store_name_store"].isin(pdv_id)]
if usuario:
    df_filtrado = df_filtrado[df_filtrado["full_name_user_provider"].isin(usuario)]
if tamano:
    df_filtrado = df_filtrado[df_filtrado["TamañoAsignado_answer"].isin(tamano)]

# ---------------------
# Navegación entre páginas
# ---------------------
if pagina == "Ejecución":
    mostrar_dashboard(df_filtrado)

elif pagina == "Lona":
    mostrar_lona(df_filtrado)

elif pagina == "Banner + Rack":
    mostrar_banner(df_filtrado)

elif pagina == "Incidencias":
    mostrar_incidencia(df_filtrado)




