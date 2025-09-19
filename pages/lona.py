import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt

def mostrar_nueva_pagina(df_filtrado):
    st.title("Lona")

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

    # --- KPIs ---
    df_filtrado = df_filtrado.copy()
    df_filtrado_lona = df_filtrado[df_filtrado["question_id_answer"].isin([1,2,3,4,8,9,10])]
    lona = df_filtrado_lona[df_filtrado_lona["question_id_answer"] == 1]["visit_id_answer"].nunique()
    finalizadas = df_filtrado_lona[df_filtrado_lona["status_visit"] == "Finalizado"]["visit_id_answer"].nunique()
    no_finalizadas = df_filtrado_lona[df_filtrado_lona["status_visit"].isin(["Pendiente", "En progreso"])]["visit_id_answer"].nunique()
    incidencias = df_filtrado_lona[df_filtrado_lona["sectionid_answer"].isin([2,5])]["visit_id_answer"].nunique()
    fotos = df_filtrado_lona[df_filtrado_lona["answer_answer"].astype(str).str.contains(".jpg", na=False)]["visit_id_answer"].count()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card("Lona", f"{lona:,}", icon="🪧")
    with col2:
        kpi_card("Finalizadas", f"{finalizadas:,}", icon="✅" )
    with col3:
        kpi_card("Finalizadas", f"{no_finalizadas:,}", icon="❌")
    with col4:
        kpi_card("Incidencias", f"{incidencias:,}", icon="🚨")
    with col5:
        kpi_card("Fotos", f"{fotos}", icon="📷")


    col1, col2 = st.columns([5, 3])  # tabla grande a la izquierda, gráficos a la derecha

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
            "visit_id_answer", "FechaHora_Menos6h_visit", "store_zone_store", "store_region_store", "name_provider", "store_name_store", "store_sap_store"
        ]].drop_duplicates()

        tabla_lona = tabla_lona.merge(info_extra, on="visit_id_answer", how="left")
        # Tu tabla ya armada
        tabla = tabla_lona.copy()
        # Ajustar altura de filas y tamaño de texto en st.dataframe
        st.markdown(
            """
            <style>
            .stDataFrame tbody tr {
                height: 80px !important;   /* grosor de las filas */
            }
            .stDataFrame tbody td div {
                font-size: 16px !important;  /* tamaño del texto */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        tabla_final = tabla[[
            "Respuesta_Antes_Lona",
            "Foto_Despues_1",
            "Foto_Despues_2",
            "FechaHora_Menos6h_visit",
            "store_zone_store",
            "store_region_store",
            "store_name_store",
            "store_sap_store",
            "Respuesta_Tamano_Lonaqr",
            "Respuesta_Tamano_Lona",
            "name_provider"
        ]]

        tabla_final.rename(columns = {
            "Respuesta_Antes_Lona": "FOTO ANTES",
            "Foto_Despues_1": "FOTO DESPUES 1",
            "Foto_Despues_2": "FOTO DESPUES 2",
            "FechaHora_Menos6h_visit": "FECHA",
            "store_zone_store": "ZONA",
            "store_region_store": "REGION",
            "store_name_store": "PDV",
            "store_sap_store": "SAP",
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
        st.dataframe(
            styled_df,
            column_config={
                "FOTO ANTES": st.column_config.ImageColumn("FOTO ANTES", width="small", ),
                "FOTO DESPUES 1": st.column_config.ImageColumn("FOTO DESPUES 1", width="small"),
                "FOTO DESPUES 2": st.column_config.ImageColumn("FOTO DESPUES 2", width="small")
            },
            use_container_width=True, height=1000
        )




    with col2:


        def chart_incidencias(df_final):
            # Filtrar incidencias (question_id = 8)
            df_inc = (
                df_final[df_final["question_id_answer"] == 8]
                .groupby("answer_answer")["visit_id_answer"]
                .nunique()
                .reset_index()
                .rename(columns={"visit_id_answer": "total"})
            )

            # Calcular porcentaje
            df_inc["porcentaje"] = (df_inc["total"] / df_inc["total"].sum() * 100).round(1)

            # Colores personalizados
            colores = ["#FF0000", "#666666", "#530C0C"]

            # Pie chart (sin hueco)
            pie = (
                alt.Chart(df_inc)
                .mark_arc()
                .encode(
                    theta=alt.Theta("total:Q"),
                    color=alt.Color(
                        "answer_answer:N",
                        scale=alt.Scale(range=colores),
                        legend=alt.Legend(title="Motivo")
                    ),
                    tooltip=[
                        alt.Tooltip("answer_answer:N", title="Motivo"),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                    ]
                )
            )


            chart = (pie 
                    .properties(
                        width=300,
                        height=300,
                        title="INCIDENCIAS"

                    )
                    .configure_title(
                        anchor="middle",   # centra el título
                        offset=15          # agrega espacio extra respecto al borde superior
                    ))

            return chart

        def chart_tamaño(df_final):
            # Filtrar incidencias (question_id = 8)
            df_inc = (
                df_final[df_final["question_id_answer"] == 4]
                .groupby("answer_answer")["visit_id_answer"]
                .nunique()
                .reset_index()
                .rename(columns={"visit_id_answer": "total"})
            )

            # Calcular porcentaje
            df_inc["porcentaje"] = (df_inc["total"] / df_inc["total"].sum() * 100).round(1)

            # Colores personalizados
            colores = ["#FF0101", "#666666", "#630404"]

            # Gráfico tipo dona
            pie = (
                alt.Chart(df_inc)
                .mark_arc( )
                .encode(
                    theta=alt.Theta("total:Q"),
                    color=alt.Color(
                        "answer_answer:N",
                        scale=alt.Scale(range=colores),
                        legend=alt.Legend(title="Tamaño")                        
                    ),
                    tooltip=[
                        alt.Tooltip("answer_answer:N", title="Tamaño"),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                    ]
                )
            )
            chart = (pie 
                    .properties(
                        width=300,
                        height=300,
                        title="TAMAÑOS"

                    )
                    .configure_title(
                        anchor="middle",   # centra el título
                        offset=15          # agrega espacio extra respecto al borde superior
                    ))

            return chart
        

        def chart_estado(df_filtrado):
            df_inc = (
                df_filtrado[df_filtrado["type_id_visit"] == 1]
                .groupby("status_visit")["visit_id_answer"]
                .nunique()
                .reset_index()
                .rename(columns={"visit_id_answer": "total"})
            )

            # Calcular porcentaje
            df_inc["porcentaje"] = (df_inc["total"] / df_inc["total"].sum() * 100).round(1)

            # Colores personalizados
            colores = ["#A71616", "#666666", "#CCCCCC",]

            # Gráfico tipo dona
            # Gráfico tipo dona
            pie = (
                alt.Chart(df_inc)
                .mark_arc( )
                .encode(
                    theta=alt.Theta("total:Q"),
                    color=alt.Color(
                        "status_visit:N",
                        scale=alt.Scale(range=colores),
                        legend=alt.Legend(title="Estado")                        
                    ),
                    tooltip=[
                        alt.Tooltip("answer_answer:N", title="Estado"),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                    ]
                )
            )
            chart = (pie 
                    .properties(
                        width=300,
                        height=300,
                        title="ESTADO DE FINALIZACIÓN"
                    )
                    .configure_title(
                        anchor="middle",   # centra el título
                        offset=15          # agrega espacio extra respecto al borde superior
                    ))
            
            return chart
        
        st.altair_chart(chart_incidencias(df_filtrado_lona), use_container_width=True)
        st.altair_chart(chart_tamaño(df_filtrado_lona), use_container_width=True)
        st.altair_chart(chart_estado(df_filtrado), use_container_width=True)


