import streamlit as st
from data_prep import load_data
import pandas as pd
from datetime import date, timedelta
from authlib.integrations.requests_client import OAuth2Session
import os
from paginas.dashboard import mostrar_dashboard
from paginas.lona import mostrar_nueva_pagina
from paginas.banner_rack import mostrar_nueva_pagina
from paginas.incidencia import mostrar_incidencia

# ---------------------
# Cargar datos
# ---------------------
df_final = load_data()

        # Menú lateral para seleccionar página
pagina = st.sidebar.selectbox(
    "Selecciona una página",
    ["Ejecución", "Lona", "Banner + Rack", "Incidencias"],
    index=0  # Los nombres de tus páginas
)


#CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
#CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8501"
#REDIRECT_URI = "https://appfemsa-eeoerf69vjjsguyqqxxpjg.streamlit.app"


AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
# ---------------------
# Función de login con Google
# ---------------------
def login_with_google():
    oauth = OAuth2Session(
        client_id=CLIENT_ID,
        scope=["openid", "email", "profile"],
        redirect_uri=REDIRECT_URI,
    )
#    st.write(st.query_params)
    if "code" in st.query_params:
        code = st.query_params["code"]
        token = oauth.fetch_token(
            TOKEN_URL,
            code=code,
            client_secret=CLIENT_SECRET
        )


        user_info = oauth.get(USER_INFO_URL).json()
        st.session_state["user_email"] = user_info["email"]
        st.session_state["user_name"] = user_info.get("name", "")
    else:
        auth_url, _ = oauth.create_authorization_url(
            AUTHORIZATION_URL, access_type="offline", prompt="consent"
        )
        st.markdown(f"[Inicia sesión con Google]({auth_url})")
# ---------------------
# Login
# ---------------------
if "user_email" not in st.session_state:
    login_with_google()
else:


    page_bg = """
        <style>
            /* Fondo y color de texto */
            body, [data-testid="stAppViewContainer"] {
                background-color: #3C3C3C;  /* Gris suave */
                color: black;               /* Texto oscuro para contraste */
            }
            .stText, .stMarkdown {
                color: black;
            }
            /* Contenedor principal full width */
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: 100% !important;
            }
        </style>
        """
    st.markdown(page_bg, unsafe_allow_html=True)

    st.success(f"Hola, {st.session_state['user_name']} ({st.session_state['user_email']})")        


    # --- Filtrar datos según el usuario ---
    user_email = st.session_state["user_email"]
    df_filtrado = df_final[df_final["email_provider"] == user_email].copy()

    if df_filtrado.empty:
        st.warning("No tienes datos asignados en la base.")
    else:
        # ---------------------
        # Barra lateral: filtros
        # ---------------------
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





        # Importar el contenido según la página
        # ---------------------
        if pagina == "Ejecución":
            from paginas.dashboard import mostrar_dashboard
            mostrar_dashboard(df_filtrado)


        elif pagina == "Lona":
            from paginas.lona import mostrar_nueva_pagina
            mostrar_nueva_pagina(df_filtrado)

        elif pagina == "Banner + Rack":
            from paginas.banner_rack import mostrar_nueva_pagina
            mostrar_nueva_pagina(df_filtrado)

        elif pagina == "Incidencias":
            from paginas.incidencia import mostrar_incidencia
            mostrar_incidencia(df_filtrado)




