import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt
import base64
from pathlib import Path

def load_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def mostrar_nueva_pagina(df_filtrado):
    st.title("Lona")

    def kpi_card(title, value, icon=None, width="100%"):
        icon_html = ""
        if icon:
            icon_path = Path(icon)
            if icon_path.exists():
                # Convertir imagen a base64
                img_base64 = load_base64_image(icon_path)
                icon_html = f"<img src='data:image/png;base64,{img_base64}' style='width:50px; height:50px; margin-right:10px;'>"
            else:
                icon_html = f"<div style='font-size: 24px; margin-right: 10px;'>{icon}</div>"

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
                <div style="font-size: 28px; font-weight: bold; color: white; margin-top: 4px;">
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




    # --- KPIs ---
    df_filtrado = df_filtrado.copy()
    df_filtrado_lona = df_filtrado[df_filtrado["type_id_visit"].isin([1])]
    lona = df_filtrado_lona[df_filtrado_lona["question_id_answer"].isin([1,2,3,4,8,9,10])]["visit_id_answer"].nunique()
    finalizadas = df_filtrado_lona[df_filtrado_lona["status_visit"] == "Finalizado"]["visit_id_answer"].nunique()
    no_finalizadas = df_filtrado_lona[df_filtrado_lona["status_visit"].isin(["Pendiente", "En progreso"])]["visit_id_answer"].nunique()
    incidencias = df_filtrado_lona[df_filtrado_lona["sectionid_answer"].isin([2,5])]["visit_id_answer"].nunique()
    fotos = df_filtrado_lona[df_filtrado_lona["answer_answer"].astype(str).str.contains(".jpg", na=False)]["visit_id_answer"].count()
    pct_finalizadas = (finalizadas / lona * 100) if lona > 0 else 0
    pct_no_finalizadas = (no_finalizadas / lona * 100) if lona > 0 else 0
    pct_incidencias = (incidencias / finalizadas * 100) if finalizadas > 0 else 0



    def kpi_cards():

    # --- Fila 1: 4 tarjetas ---
        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("Lona", f"{lona:,}", icon="imagenes/localizacion.png")
        with col2:
            kpi_card("Finalizadas", f"{finalizadas:,}", icon="imagenes/garrapata.png")
        with col3:
            kpi_card("No Finalizadas", f"{no_finalizadas:,}", icon="imagenes/cancelar.png")

        # --- Fila 2: 5 tarjetas (con 2 porcentajes en la misma) ---
        col5, col6, col_pct = st.columns([1, 1, 1])

        with col5:
            kpi_card("Fotos", f"{fotos:,}", icon="imagenes/galeria-de-imagenes (1).png")
        with col6:
            kpi_card("Incidencias", f"{incidencias:,}", icon="imagenes/advertencia.png")



        # Tarjeta con dos porcentajes (dividida en dos mitades)
        with col_pct:
            kpi_card_double("% Finalizadas", f"{pct_finalizadas:.1f}%", "% Incidencias", f"{pct_incidencias:.1f}%")
    
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
            x=alt.X(
                        "fecha_visit:T",
                        title="Fecha",
                        axis=alt.Axis(format="%b %d")  # ✅ Muestra 'Sep 07', 'Oct 02', etc.
                    ),
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
        kpi_cards()
    with con2:
        st.altair_chart(ejecucion_por_dia(df_filtrado_lona), use_container_width=True)




    col1, col2 = st.columns([5, 2])  # tabla grande a la izquierda, gráficos a la derecha

    with col1:



        antes_lona = df_filtrado_lona.loc[df_filtrado_lona["question_id_answer"] == 1, ["visit_id_answer", "answer_answer"]]
        antes_lona = antes_lona.groupby("visit_id_answer")["answer_answer"].max().reset_index()
        antes_lona.rename(columns={"answer_answer": "Respuesta_Antes_Lona"}, inplace=True)

        foto1 = df_filtrado_lona[df_filtrado_lona["question_id_answer"] == 2].dropna(subset=["answer_answer"])
        foto1 = foto1.sort_values(["visit_id_answer", "id_answer"]).groupby("visit_id_answer").first().reset_index()
        foto1 = foto1[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_1"})

        foto2 = df_filtrado_lona[df_filtrado_lona["question_id_answer"] == 2].dropna(subset=["answer_answer"])
        foto2 = (
            foto2.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .nth(1)   # la segunda fila (índice 1)
            .reset_index()
        )
        foto2 = foto2[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_2"})

        tamano = df_filtrado_lona.loc[df_filtrado_lona["question_id_answer"] == 4, ["visit_id_answer", "answer_answer"]]
        tamano = tamano.groupby("visit_id_answer")["answer_answer"].max().reset_index()
        tamano.rename(columns={"answer_answer": "Respuesta_Tamano_Lona"}, inplace=True)

        tamano_qr = df_filtrado_lona.loc[df_filtrado_lona["question_id_answer"] == 3, ["visit_id_answer", "answer_answer"]]
        tamano_qr = tamano_qr.groupby("visit_id_answer")["answer_answer"].max().reset_index()
        tamano_qr.rename(columns={"answer_answer": "Respuesta_Tamano_Lonaqr"}, inplace=True)



                # Juntar todo por visit_id_answer
        tabla_lona = antes_lona.merge(foto1, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(foto2, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(tamano, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(tamano_qr, on="visit_id_answer", how="left")

        # Agregar columnas directas desde df_final
        info_extra = df_filtrado_lona[[
            "id_visit", "status_visit", "FechaHora_Menos6h_visit", "store_zone_store", "store_region_store", "name_provider", "store_name_store", "store_sap_store"
        ]].drop_duplicates()

        tabla_lona = info_extra.merge(
            tabla_lona,
            left_on=["id_visit"],   # columna clave en tabla_lona
            right_on=["visit_id_answer"],   # columna clave en info_extra
            how="left"
        )
        # Tu tabla ya armada
        tabla = tabla_lona.copy()
        # Ajustar altura de filas y tamaño de texto en st.dataframe
        # st.markdown(
        #   """
        #   <style>
        #   .stDataFrame tbody tr {
        #      height: 80px !important;   /* grosor de las filas */
        #    }
        #    .stDataFrame tbody td div {
        #        font-size: 16px !important;  /* tamaño del texto */
        #    }
        #    </style>
        
        #   """,
        #   unsafe_allow_html=True
        #)
        tabla_final = tabla[[
            "Respuesta_Antes_Lona",
            "Foto_Despues_1",
            "Foto_Despues_2",
            "FechaHora_Menos6h_visit",
            "store_zone_store",
            "store_region_store",
            "store_name_store",
            "store_sap_store",
            "status_visit",
            "Respuesta_Tamano_Lonaqr",
            "Respuesta_Tamano_Lona",
            "name_provider"
        ]]

        tabla_final.rename(columns = {
            "Respuesta_Antes_Lona": "ANTES",
            "Foto_Despues_1": "DESPUES 1",
            "Foto_Despues_2": "DESPUES 2",
            "FechaHora_Menos6h_visit": "FECHA",
            "store_zone_store": "ZONA",
            "store_region_store": "REGION",
            "store_name_store": "PDV",
            "store_sap_store": "SAP",
            "status_visit": "ESTADO",
            "Respuesta_Tamano_Lonaqr": "TAMAÑO QR",
            "Respuesta_Tamano_Lona": "TAMAÑO SEL",
            "name_provider": "PROVEEDOR"
        }, inplace=True)

        # Aplicar estilo para aumentar altura de filas
        styled_df = tabla_final.style.set_properties(**{
            'height': '200px',  # alto de la fila
            'line-height': '50px'  # también ajusta el texto vertical
        })


        # Mostrar tu tabla
        with st.container(border=True):

            st.dataframe(
                styled_df,
                column_config={
                    "ANTES": st.column_config.ImageColumn("ANTES", width="small", ),
                    "DESPUES 1": st.column_config.ImageColumn("DESPUES 1", width="small"),
                    "DESPUES 2": st.column_config.ImageColumn("DESPUES 2", width="small")
                },
                use_container_width=True, height=500
            )


        def grafico_ejecucion_por_preventa(df_filtrado):
            # --- Filtrar solo Lona ---
            df_lona = df_filtrado[df_filtrado["type_id_visit"].isin([1])]

            # --- Calcular totales por preventa ---
            col_preventa = "name_provider"  # 🔁 cambia si tu columna tiene otro nombre

            total_por_preventa = (
                df_lona.groupby(col_preventa)["visit_id_answer"]
                .nunique()
                .reset_index(name="Total")
            )

            finalizadas_por_preventa = (
                df_lona[df_lona["status_visit"] == "Finalizado"]
                .groupby(col_preventa)["visit_id_answer"]
                .nunique()
                .reset_index(name="Finalizadas")
            )

            # --- Unir y calcular % de ejecución ---
            ejecucion = pd.merge(total_por_preventa, finalizadas_por_preventa, on=col_preventa, how="left").fillna(0)
            ejecucion["% Ejecución"] = (ejecucion["Finalizadas"] / ejecucion["Total"]) * 100

            # --- Gráfico horizontal con Altair ---
            bars = alt.Chart(ejecucion).mark_bar(
                color="#666666",  # azul corporativo
                cornerRadiusTopRight=3,
                cornerRadiusBottomRight=3
            ).encode(
                y=alt.Y(f"{col_preventa}:N", sort='-x', title="Proveedor"),
                x=alt.X("% Ejecución:Q", title="% Ejecución", scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip(f"{col_preventa}:N", title="Proveedor"),
                    alt.Tooltip("% Ejecución:Q", format=".1f", title="% Ejecución"),
                    alt.Tooltip("Finalizadas:Q", title="Finalizadas"),
                    alt.Tooltip("Total:Q", title="Total")
                ]
            )

            # --- Texto con porcentaje ---
            text = alt.Chart(ejecucion).mark_text(
                align='left',
                baseline='middle',
                dx=5,
                color='black'
            ).encode(
                y=f"{col_preventa}:N",
                x="% Ejecución:Q",
                text=alt.Text("% Ejecución:Q", format=".1f")
            )

            chart = (bars + text).properties(
                width=600,
                height=250,
                title="% de Ejecución por Proveedor",
                background="transparent"
            ).configure_view(
                stroke=None
            ).configure_title(
                fontSize=22,
                fontWeight="bold",
                anchor="start",
                color="#000000"
            ).configure_axis(
                labelColor="#000000",
                titleColor="#000000"
            )

            return chart
        
        with st.container(border=True):
            st.altair_chart(grafico_ejecucion_por_preventa(df_filtrado), use_container_width=True)



    with col2:

        def chart_pie(df, group_col, title, colors, legend_title):
            df_grouped = (
                df.groupby(group_col)["visit_id_answer"]
                .nunique()
                .reset_index()
                .rename(columns={"visit_id_answer": "total"})
            )
            df_grouped["porcentaje"] = (df_grouped["total"] / df_grouped["total"].sum() * 100).round(1)

            pie = alt.Chart(df_grouped).mark_arc().encode(
                theta=alt.Theta("total:Q"),
                color=alt.Color(
                    f"{group_col}:N",
                    scale=alt.Scale(range=colors),
                    legend=alt.Legend(title=legend_title)
                ),
                tooltip=[
                    alt.Tooltip(f"{group_col}:N", title=legend_title),
                    alt.Tooltip("total:Q", title="Total"),
                    alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                ]
            )


            
            return (
                pie.properties(
                    width=300,
                    height=230,
                    title=title,
                    background="transparent"
                )
                .configure_title(
                    fontSize=22, fontWeight="bold", anchor="start", color="#000000"
                )
                .configure_legend(
                    labelColor="#000000",
                    titleColor="#000000",
                    labelFontSize=13,
                    titleFontSize=14
                )
            )
        with st.container(border=True):
            st.altair_chart(chart_pie(df_filtrado_lona[df_filtrado_lona["question_id_answer"] == 8], "answer_answer", "Incidencias", ["#FF0000", "#666666", "#530C0C"], "Motivo"), use_container_width=True)
        with st.container(border=True):
            st.altair_chart(chart_pie(df_filtrado_lona[df_filtrado_lona["question_id_answer"] == 4], "answer_answer", "Tamaños", ["#FF0101", "#666666", "#630404"], "Tamaño"), use_container_width=True)
        with st.container(border=True):        
            st.altair_chart(chart_pie(df_filtrado_lona[df_filtrado_lona["type_id_visit"] == 1], "status_visit", "Estado de Finalización", ["#A71616", "#666666", "#CCCCCC"], "Estado"), use_container_width=True)

