import streamlit as st
from data_prep import load_data
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

def mostrar_dashboard(df_filtrado):


    if len(df_filtrado) == 0:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return
    # --- KPI Cards ---
    def kpi_card(title, value, icon=None, width="100%"):
        icon_html = f"<div style='font-size: 20px; margin-right: 10px;'>{icon}</div>" if icon else ""
        
        card_html = f"""
        <div style="
            background-color: #111;  
            border-radius: 12px;
            padding: 12px;
            margin: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            height: 90px;
            width: {width};
            box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
        ">
            {icon_html}
            <div style="text-align: center; width: 100%;">
                <div style="font-size: 12px; font-weight: bold; color: white;">
                    {title}
                </div>
                <div style="font-size: 22px; font-weight: bold; color: white; margin-top: 4px;">
                    {value}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    def kpi_card_double(title1, value1, title2, value2):
        card_html = f"""
        <div style="
            background-color: #111;  
            border-radius: 12px;
            padding: 12px;
            margin: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            height: 90px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
        ">
            <div style="text-align: center; width: 50%;">
                <div style="font-size: 12px; font-weight: bold; color: white;">
                    {title1}
                </div>
                <div style="font-size: 22px; font-weight: bold; color: white; margin-top: 4px;">
                    {value1}
                </div>
            </div>
            <div style="text-align: center; width: 50%; border-left: 1px solid gray;">
                <div style="font-size: 12px; font-weight: bold; color: white;">
                    {title2}
                </div>
                <div style="font-size: 22px; font-weight: bold; color: white; margin-top: 4px;">
                    {value2}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


    def kpi_cards(df_final):
        universo_pdv = df_final["id_visit"].nunique()
        lona = df_final[df_final["question_id_answer"].isin([1,2,3,4,8,9,10])]["visit_id_answer"].nunique()
        finalizadas = df_final[df_final["status_visit"] == "Finalizado"]["visit_id_answer"].nunique()
        no_finalizadas = df_final[df_final["status_visit"].isin(["Pendiente", "En progreso"])]["visit_id_answer"].nunique()
        banner_rack = df_final[df_final["question_id_answer"].isin([5,6,7,11,13,15,17,14,16,12])]["visit_id_answer"].nunique()
        incidencia = df_final[df_final["sectionid_answer"].isin([2,5])]["visit_id_answer"].nunique()
        fotos = df_final[df_final["answer_answer"].astype(str).str.contains(".jpg", na=False)]["visit_id_answer"].count()

        pct_finalizadas = (finalizadas / universo_pdv * 100) if universo_pdv > 0 else 0
        pct_no_finalizadas = (no_finalizadas / universo_pdv * 100) if universo_pdv > 0 else 0

    # --- Fila 1: 4 tarjetas ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            kpi_card("Lona", f"{lona:,}", icon="🪧")
        with col2:
            kpi_card("Banner + Rack", f"{banner_rack:,}", icon="🖼️" )
        with col3:
            kpi_card("Incidencias", f"{incidencia:,}", icon="🚨")
        with col4:
            kpi_card("Fotos", f"{fotos:,}", icon="📷")

        # --- Fila 2: 5 tarjetas (con 2 porcentajes en la misma) ---
        col5, col6, col7, col_pct = st.columns([1, 1, 1, 1])

        with col5:
            kpi_card("Universo PDV", f"{universo_pdv:,}", icon="🏪")
        with col6:
            kpi_card("Finalizadas", f"{finalizadas:,}", icon="✅")
        with col7:
            kpi_card("No Finalizadas", f"{no_finalizadas:,}", icon="❌")


        # Tarjeta con dos porcentajes (dividida en dos mitades)
        with col_pct:
            kpi_card_double("% Finalizadas", f"{pct_finalizadas:.1f}%", "% No Finalizadas", f"{pct_no_finalizadas:.1f}%")


    # --- Gráfico de ejecución por día ---

    def ejecucion_por_dia(df_final):
        df_hist = (
            df_final.groupby("fecha_visit")["visit_id_answer"]
            .nunique()
            .reset_index()
            .rename(columns={"visit_id_answer": "total_ejecucion"})
        )

        bars = alt.Chart(df_hist).mark_bar(
            color="#AF0E0E", size=25,
            cornerRadiusTopLeft=3, cornerRadiusTopRight=3
        ).encode(
            x=alt.X("fecha_visit:T", title="Fecha"),
            y=alt.Y("total_ejecucion:Q", title="PDV Medidos"),
            tooltip=[
                alt.Tooltip("fecha_visit:T", title="Fecha", format="%b %d, %Y"),  # ✅ fecha formateada
                alt.Tooltip("total_ejecucion:Q", title="PDV Medidos")              # ✅ nombre más claro
            ]
        )

        text = alt.Chart(df_hist).mark_text(
            dy=-10, color="black", size=14
        ).encode(
            x="fecha_visit:T",
            y="total_ejecucion:Q",
            text="total_ejecucion:Q"
        )
        chart = (bars + text).properties(
            width=500,
            height=200,
            title="Histórico de Ejecución por Día",
            background="transparent"  # sin fondo blanco
        ).configure_view(
            stroke=None
            ).configure_title(
                fontSize=22,
                fontWeight="bold",
                anchor="start",
                color="#000000"  # negro para el título
            ).configure_axis(
                labelColor="#000000",  # negro para etiquetas de ejes
                titleColor="#000000"   # negro para títulos de ejes
            ).configure_legend(
                labelColor="#000000",
                titleColor="#000000"
            )

        return chart



    # --- Layout KPIs + gráfico ---
    col1, col2 = st.columns([3, 2])
    
    con2 = col2.container(border=True)
    with col1:
        kpi_cards(df_filtrado)
    with con2:
        st.altair_chart(ejecucion_por_dia(df_filtrado), use_container_width=True)



    # --- Tabla matriz ---
    # Visitas Únicas
    tabla = df_filtrado.drop_duplicates(subset=["id_visit"])[[
            "id_visit",
            "store_sap_store",
            "store_name_store",
            "store_zone_store",
            "store_region_store",
            "name_type",
            "FechaHora_Menos6h_visit",
            "status_visit",
            "name_provider"

    ]]

    #-- incidencias
    incidencias = df_filtrado[df_filtrado["sectionid_answer"].isin([2,5])] #Se utiliza isin para filtrar los valores de la encuesta que tengan ese valor
    incidencias = incidencias.groupby("id_visit").size().reset_index(name="count_incidencias") #cuenta la cantidad de incidencias que hay en cada visita y lo vuelve dataframe
    incidencias["TieneIncidencia"] = incidencias["count_incidencias"].apply(lambda x: "Sí" if x > 0 else "No")

    tabla = tabla.merge(incidencias[["id_visit", "TieneIncidencia"]], 
                        on="id_visit", 
                        how="left")
    
    #-- motivo
    motivo = df_filtrado[df_filtrado["question_id_answer"].isin([8,5])]
    motivo = motivo.groupby("id_visit")["answer_answer"].first().reset_index(name="Respuesta_motivo")
    tabla = tabla.merge(motivo, 
                        on="id_visit", 
                        how="left")
    
    tamaño = df_filtrado[df_filtrado["question_id_answer"].isin([4,14])]
    tamaño = tamaño.groupby("id_visit")["answer_answer"].first().reset_index(name="tamaño")
    tabla = tabla.merge(tamaño,
                        on="id_visit",
                        how = "left")
    
    comentario = df_filtrado[df_filtrado["question_id_answer"].isin([7, 10])]
    comentario = comentario.groupby("id_visit")["answer_answer"].first().reset_index(name = "comentario")
    tabla = tabla.merge(comentario,
                        on="id_visit",
                        how = "left")
    
    tabla_final = tabla[[
        "store_sap_store",
        "store_name_store",
        "store_zone_store",
        "store_region_store",
        "name_type",
        "FechaHora_Menos6h_visit",
        "status_visit",
        "TieneIncidencia",
        "Respuesta_motivo",
        "name_provider",
        "tamaño",
        "comentario"
    ]]

    # --- Seleccionar y renombrar columnas finales ---
    tabla_final.rename(columns={
        "store_sap_store": "SAP",
        "store_name_store": "PDV",
        "store_zone_store": "ZONA",
        "store_region_store": "REGION",
        "name_type": "CATEGORÍA",
        "FechaHora_Menos6h_visit": "FECHA VISITA",
        "status_visit": "ESTADO",
        "TieneIncidencia": "TIENE INCIDENCIA",
        "Respuesta_motivo": "MOTIVO",
        "name_provider": "PROVEEDOR",
        "tamaño": "TAMAÑO",
        "comentario": "COMENTARIO"
    }, inplace=True)

    
    # --- Mostrar con scroll ---
    with st.container(border=True):
        st.markdown("### Tabla de Visitas Detallada")
        st.dataframe(tabla_final, use_container_width=True, height=500)

    






