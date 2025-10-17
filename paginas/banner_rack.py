import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import altair as alt

def mostrar_nueva_pagina(df_filtrado):
    st.title("Banner + Rack")

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
    df_filtrado_lona = df_filtrado[df_filtrado["type_id_visit"].isin([2])]
    lona = df_filtrado_lona[df_filtrado_lona["question_id_answer"].isin([5,6,7,11,13,15,17,14,16,12])]["visit_id_answer"].nunique()
    finalizadas = df_filtrado_lona[df_filtrado_lona["status_visit"] == "Finalizado"]["visit_id_answer"].nunique()
    no_finalizadas = df_filtrado_lona[df_filtrado_lona["status_visit"].isin(["Pendiente", "En progreso"])]["visit_id_answer"].nunique()
    incidencias = df_filtrado_lona[df_filtrado_lona["sectionid_answer"].isin([2,5])]["visit_id_answer"].nunique()
    fotos = df_filtrado_lona[df_filtrado_lona["answer_answer"].astype(str).str.contains(".jpg", na=False)]["visit_id_answer"].count()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card("Banner + Rack", f"{lona:,}", icon="🪧")
    with col2:
        kpi_card("Finalizadas", f"{finalizadas:,}", icon="✅" )
    with col3:
        kpi_card("No Finalizadas", f"{no_finalizadas:,}", icon="❌")
    with col4:
        kpi_card("Incidencias", f"{incidencias:,}", icon="🚨")
    with col5:
        kpi_card("Fotos", f"{fotos}", icon="📷")


    col1, col2 = st.columns([5, 3],  vertical_alignment="top") # tabla grande a la izquierda, gráficos a la derecha

    with col1:


        foto1_banner = df_filtrado_lona.loc[df_filtrado_lona["question_id_answer"] == 12].dropna(subset=["answer_answer"])
        foto1_banner = (
            foto1_banner.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .first()   # primer registro
            .reset_index()
        )
        foto1_banner = foto1_banner[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_1banner"})

        foto2_banner = df_filtrado_lona[df_filtrado_lona["question_id_answer"] == 12].dropna(subset=["answer_answer"])
        foto2_banner = (
            foto2_banner.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .nth(1)   # <- segunda fila (índice 1)
            .reset_index()
        )
        foto2_banner = foto2_banner[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_2banner"})

        
        foto1_rack = df_filtrado_lona.loc[df_filtrado_lona["question_id_answer"] == 16].dropna(subset=["answer_answer"])
        foto1_rack = (
            foto1_rack.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .first()   # primer registro
            .reset_index()
        )
        foto1_rack = foto1_rack[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_1rack"})


        tamano_bannerqr = df_filtrado_lona.loc[
            (df_filtrado_lona["question_id_answer"] == 13) & 
            (df_filtrado_lona["answer_answer"].notna()), 
            ["visit_id_answer", "answer_answer"]
        ]

        tamano_bannerqr = (
            tamano_bannerqr.groupby("visit_id_answer")["answer_answer"]
            .max()
            .reset_index()
            .rename(columns={"answer_answer": "Respuesta_Tamano_bannerqr"})
        )

        tamano_banner = df_filtrado_lona.loc[
            (df_filtrado_lona["question_id_answer"] == 14) & 
            (df_filtrado_lona["answer_answer"].notna()), 
            ["visit_id_answer", "answer_answer"]
        ]

        tamano_banner = (
            tamano_banner.groupby("visit_id_answer")["answer_answer"]
            .max()
            .reset_index()
            .rename(columns={"answer_answer": "Respuesta_Tamano_banner"})
        )

        posicion_rack = df_filtrado_lona.loc[
            (df_filtrado_lona["question_id_answer"] == 17) & 
            (df_filtrado_lona["answer_answer"].notna()), 
            ["visit_id_answer", "answer_answer"]
        ]

        posicion_rack = (
            posicion_rack.groupby("visit_id_answer")["answer_answer"]
            .max()
            .reset_index()
            .rename(columns={"answer_answer": "Posicion_Rack"})
        )



                # Juntar todo por visit_id_answer
        tabla_lona = foto1_banner.merge(foto2_banner, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(foto1_rack, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(tamano_bannerqr, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(tamano_banner, on="visit_id_answer", how="left")
        tabla_lona = tabla_lona.merge(posicion_rack, on="visit_id_answer", how="left")

        # Agregar columnas directas desde df_final
        info_extra = df_filtrado_lona[[
            "visit_id_answer", "FechaHora_Menos6h_visit", "store_zone_store", "store_region_store", "name_provider", "store_name_store", "store_sap_store"
        ]].drop_duplicates()

        tabla_lona = tabla_lona.merge(info_extra, on="visit_id_answer", how="left")
        # Tu tabla ya armada
        tabla = tabla_lona.copy()
        # Ajustar altura de filas y tamaño de texto en st.dataframe

        tabla_final = tabla[[
            "Foto_Despues_1banner",
            "Foto_Despues_2banner",
            "Foto_Despues_1rack",
            "FechaHora_Menos6h_visit",
            "store_zone_store",
            "store_region_store",
            "store_name_store",
            "store_sap_store",
            "Respuesta_Tamano_bannerqr",
            "Respuesta_Tamano_banner",
            "Posicion_Rack",
            "name_provider"
        ]]

        tabla_final.rename(columns = {
            "Foto_Despues_1banner": "BANNER FOTO DESPUÉS 1",
            "Foto_Despues_2banner": "BANNER FOTO DESPUÉS 2",
            "Foto_Despues_1rack": "RACK FOTO DESPUÉS 1",
            "FechaHora_Menos6h_visit": "FECHA",
            "store_zone_store": "ZONA",
            "store_region_store": "REGION",
            "store_name_store": "PDV",
            "store_sap_store": "SAP",
            "Respuesta_Tamano_bannerqr": "TAMAÑO QR",
            "Respuesta_Tamano_banner": "TAMAÑO SEL",
            "Posicion_Rack": "POSICIÓN RACK",
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
                    "FOTO ANTES": st.column_config.ImageColumn("FOTO ANTES", width="small", ),
                    "FOTO DESPUES 1": st.column_config.ImageColumn("FOTO DESPUES 1", width="small"),
                    "FOTO DESPUES 2": st.column_config.ImageColumn("FOTO DESPUES 2", width="small")
                },
                use_container_width=True, height=1150
            )




    with col2:


        def chart_incidencias(df_final):
            # Filtrar incidencias (question_id = 8)
            df_inc = (
                df_final[df_final["question_id_answer"] == 5]
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
                        height=250,
                        title="Incidencias",
                        background="transparent"
                    )
                    .configure_title(
                            fontSize=22,
                            fontWeight="bold",
                            anchor="start",
                            color="#000000"  # negro
                        )
                        .configure_legend(
                            labelColor="#000000",   # color de texto de las etiquetas
                            titleColor="#000000",   # color del título de la leyenda
                            labelFontSize=13,
                            titleFontSize=14
        )
                    )

            return chart

        def chart_tamaño(df_final):
            # Filtrar incidencias (question_id = 8)
            df_inc = (
                df_final[df_final["question_id_answer"] == 14]
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
                        height=250,
                        title="Tamaños",
                        background="transparent"
                    )
                    .configure_title(
                            fontSize=22,
                            fontWeight="bold",
                            anchor="start",
                            color="#000000"  # negro
                        )
                        .configure_legend(
                            labelColor="#000000",   # color de texto de las etiquetas
                            titleColor="#000000",   # color del título de la leyenda
                            labelFontSize=13,
                            titleFontSize=14
        )
                    )
            return chart
        
        def chart_posición(df_final):
            # Filtrar incidencias (question_id = 8)
            df_inc = (
                df_final[df_final["question_id_answer"] == 17]
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
                        legend=alt.Legend(title="Posición")                        
                    ),
                    tooltip=[
                        alt.Tooltip("answer_answer:N", title="Posición"),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                    ]
                )
            )
            chart = (pie 
                    .properties(
                        width=300,
                        height=250,
                        title="Posición",
                        background="transparent"
                    )
                    .configure_title(
                            fontSize=22,
                            fontWeight="bold",
                            anchor="start",
                            color="#000000"  # negro
                        )
                        .configure_legend(
                            labelColor="#000000",   # color de texto de las etiquetas
                            titleColor="#000000",   # color del título de la leyenda
                            labelFontSize=13,
                            titleFontSize=14
        )
                    )

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
                        alt.Tooltip("status_visit:N", title="Estado"),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                    ]
                )
            )
            chart = (pie 
                    .properties(
                        width=300,
                        height=250,
                        title="Estado de Finalización",
                        background="transparent"
                    )
                    .configure_title(
                            fontSize=22,
                            fontWeight="bold",
                            anchor="start",
                            color="#000000"  # negro
                        )
                        .configure_legend(
                            labelColor="#000000",   # color de texto de las etiquetas
                            titleColor="#000000",   # color del título de la leyenda
                            labelFontSize=13,
                            titleFontSize=14
        )
                    )
            return chart
        with st.container(border=True):
            st.altair_chart(chart_incidencias(df_filtrado_lona), use_container_width=True)
        with st.container(border=True):
            st.altair_chart(chart_tamaño(df_filtrado_lona), use_container_width=True)
        with st.container(border=True):
            st.altair_chart(chart_posición(df_filtrado_lona), use_container_width=True)
        with st.container(border=True):
            st.altair_chart(chart_estado(df_filtrado_lona), use_container_width=True)


