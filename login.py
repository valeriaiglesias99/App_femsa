import pandas as pd
from connection import get_connection 
import numpy as np
import streamlit as st


def validar_usuario(usuario, clave):
    """
    Valida usuario usando el email como usuario y contraseña.
    """
    query = """
        SELECT email, name
        FROM providers
        WHERE email = %s
    """

    conn = get_connection()
    df = pd.read_sql(query, conn, params=(usuario,))
    conn.close()

    # Si existe usuario, validar clave (que es el mismo email)
    if len(df) > 0 and usuario == clave:
        return True, df["name"].iloc[0]

    return False, None

def mostrar_login():


    # Si ya hay usuario logueado → saltar login
    if "usuario" in st.session_state:
        return True

    with st.form("login_form"):
        usuario = st.text_input("Email")
        clave = st.text_input("Contraseña", type="password")
        btn = st.form_submit_button("Ingresar")

        if btn:
            valido, nombre = validar_usuario(usuario, clave)

            if valido:
                st.session_state.usuario = usuario
                st.session_state.nombre = nombre
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    return False