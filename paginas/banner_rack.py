import streamlit as st
import pandas as pd
import altair as alt
import base64
from pathlib import Path

def load_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def mostrar_nueva_pagina(df_filtrado):
    st.title("Banner + Rack")

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
    df_filtrado_banner = df_filtrado[df_filtrado["type_id_visit"].isin([2])]
    df_filtrado_banner_conteo = df_filtrado_banner["id_visit"].nunique()
    banner = df_filtrado_banner[df_filtrado_banner["question_id_answer"].isin([5,6,7,11,13,15,17,14,16,12])]["visit_id_answer"].nunique()
    finalizadas = df_filtrado_banner[df_filtrado_banner["status_visit"] == "Finalizado"]["id_visit"].nunique()
    no_finalizadas = df_filtrado_banner[df_filtrado_banner["status_visit"] != "Finalizado"]["id_visit"].nunique()
    incidencias = df_filtrado_banner[df_filtrado_banner["id_section"].isin([2,5])]["visit_id_answer"].nunique()
    fotos = df_filtrado_banner[df_filtrado_banner["answer_answer"].astype(str).str.contains(".jpg", na=False)]["visit_id_answer"].count()
    pct_finalizadas = (finalizadas / df_filtrado_banner_conteo * 100) if df_filtrado_banner_conteo > 0 else 0
    pct_no_finalizadas = (no_finalizadas / df_filtrado_banner_conteo * 100) if df_filtrado_banner_conteo > 0 else 0
    pct_incidencias = (incidencias / finalizadas * 100) if finalizadas > 0 else 0


    def kpi_cards():

    # --- Fila 1: 4 tarjetas ---
        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("Banner", f"{df_filtrado_banner_conteo:,}", icon="imagenes/localizacion.png")
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

        finalizadas = df_final[df_final["status_visit"] == "Finalizado"]

        df_hist = (
            finalizadas.groupby("Fecha_Menos6h_visit")["id_visit"]
            .nunique()
            .reset_index()
            .rename(columns={"id_visit": "total_ejecucion"})
        )

        bars = alt.Chart(df_hist).mark_bar(
            color="#AF0E0E", size=20,
            cornerRadiusTopLeft=3, cornerRadiusTopRight=3
        ).encode(
            x=alt.X(
                        "Fecha_Menos6h_visit:T",
                        title="Fecha",
                        axis=alt.Axis(format="%b %d")
                                    ),
            y=alt.Y("total_ejecucion:Q", title="PDV Medidos"),
            tooltip=[
                alt.Tooltip("Fecha_Menos6h_visit:T", title="Fecha", format="%b %d, %Y"),  # ✅ fecha formateada
                alt.Tooltip("total_ejecucion:Q", title="PDV Medidos")              # ✅ nombre más claro
            ])


        text = alt.Chart(df_hist).mark_text(
            dy=-10, color="black", size=14
        ).encode(
            x="Fecha_Menos6h_visit:T",
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
            ).configure_bar(
                    binSpacing=12        # ESPACIO ENTRE BARRAS
                )

        return chart



    # --- Layout KPIs + gráfico ---
    col1, col2 = st.columns([3, 2])
    
    con2 = col2.container(border=True)
    with col1:
        kpi_cards()
    with con2:
        st.altair_chart(ejecucion_por_dia(df_filtrado_banner), use_container_width=True)



    col1, col2 = st.columns([5, 2],  vertical_alignment="top") # tabla grande a la izquierda, gráficos a la derecha

    with col1:


        foto1_banner = df_filtrado_banner.loc[df_filtrado_banner["question_id_answer"] == 12].dropna(subset=["answer_answer"])
        foto1_banner = (
            foto1_banner.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .first()   # primer registro
            .reset_index()
        )
        foto1_banner = foto1_banner[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_1banner"})

        foto2_banner = df_filtrado_banner[df_filtrado_banner["question_id_answer"] == 12].dropna(subset=["answer_answer"])
        foto2_banner = (
            foto2_banner.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .nth(1)   # <- segunda fila (índice 1)
            .reset_index()
        )
        foto2_banner = foto2_banner[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_2banner"})

        
        foto1_rack = df_filtrado_banner.loc[df_filtrado_banner["question_id_answer"] == 16].dropna(subset=["answer_answer"])
        foto1_rack = (
            foto1_rack.sort_values(["visit_id_answer", "id_answer"])
            .groupby("visit_id_answer")
            .first()   # primer registro
            .reset_index()
        )
        foto1_rack = foto1_rack[["visit_id_answer", "answer_answer"]].rename(columns={"answer_answer": "Foto_Despues_1rack"})


        tamano_bannerqr = df_filtrado_banner.loc[
            (df_filtrado_banner["question_id_answer"] == 13) & 
            (df_filtrado_banner["answer_answer"].notna()), 
            ["visit_id_answer", "answer_answer"]
        ]

        tamano_bannerqr = (
            tamano_bannerqr.groupby("visit_id_answer")["answer_answer"]
            .max()
            .reset_index()
            .rename(columns={"answer_answer": "Respuesta_Tamano_bannerqr"})
        )

        tamano_banner = df_filtrado_banner.loc[
            (df_filtrado_banner["question_id_answer"] == 14) & 
            (df_filtrado_banner["answer_answer"].notna()), 
            ["visit_id_answer", "answer_answer"]
        ]

        tamano_banner = (
            tamano_banner.groupby("visit_id_answer")["answer_answer"]
            .max()
            .reset_index()
            .rename(columns={"answer_answer": "Respuesta_Tamano_banner"})
        )

        posicion_rack = df_filtrado_banner.loc[
            (df_filtrado_banner["question_id_answer"] == 17) & 
            (df_filtrado_banner["answer_answer"].notna()), 
            ["visit_id_answer", "answer_answer"]
        ]

        posicion_rack = (
            posicion_rack.groupby("visit_id_answer")["answer_answer"]
            .max()
            .reset_index()
            .rename(columns={"answer_answer": "Posicion_Rack"})
        )



                # Juntar todo por visit_id_answer
        tabla_banner = foto1_banner.merge(foto2_banner, on="visit_id_answer", how="left")
        tabla_banner = tabla_banner.merge(foto1_rack, on="visit_id_answer", how="left")
        tabla_banner = tabla_banner.merge(tamano_bannerqr, on="visit_id_answer", how="left")
        tabla_banner = tabla_banner.merge(tamano_banner, on="visit_id_answer", how="left")
        tabla_banner = tabla_banner.merge(posicion_rack, on="visit_id_answer", how="left")

          # Agregar columnas directas desde df_final
        info_extra = df_filtrado_banner[[
            "id_visit", "status_visit", "FechaHora_Menos6h_visit", "store_zone_store", "store_region_store", "name_provider", "store_name_store", "store_sap_store"
        ]].drop_duplicates()

        tabla_banner = info_extra.merge(
            tabla_banner,
            left_on=["id_visit"],   # columna clave en tabla_banner
            right_on=["visit_id_answer"],   # columna clave en info_extra
            how="left"
        )
        #
        tabla = tabla_banner.copy()
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
            "status_visit",
            "Respuesta_Tamano_bannerqr",
            "Respuesta_Tamano_banner",
            "Posicion_Rack",
            "name_provider"
        ]]

        tabla_final.rename(columns = {
            "Foto_Despues_1banner": "B. DESPUÉS 1",
            "Foto_Despues_2banner": "B. DESPUÉS 2",
            "Foto_Despues_1rack": "R. DESPUÉS 1",
            "FechaHora_Menos6h_visit": "FECHA",
            "store_zone_store": "ZONA",
            "store_region_store": "REGION",
            "store_name_store": "PDV",
            "store_sap_store": "SAP",
            "status_visit": "ESTADO",
            "Respuesta_Tamano_bannerqr": "TAMAÑO QR",
            "Respuesta_Tamano_banner": "TAMAÑO SEL",
            "Posicion_Rack": "POSICIÓN RACK",
            "name_provider": "PROVEEDOR"
        }, inplace=True)

        # Aplicar estilo para aumentar altura de filas
        #styled_df = tabla_final.style.set_properties(**{
        #    'height': '200px',  # alto de la fila
        #    'line-height': '50px'  # también ajusta el texto vertical
        #})


        # Mostrar tu tabla
        with st.container(border=True):

            st.dataframe(
                tabla_final,
                column_config={
                    "B. DESPUÉS 1": st.column_config.ImageColumn("B. DESPUÉS 1", width="small", ),
                    "B. DESPUÉS 2": st.column_config.ImageColumn("B. DESPUÉS 2", width="small"),
                    "R. DESPUÉS 1": st.column_config.ImageColumn("R. DESPUÉS 1", width="small")
                },
                use_container_width=True, height=650
            )

        def grafico_ejecucion_por_preventa(df_banner):

            # --- Calcular totales por preventa ---
            col_preventa = "email_user"  

            total_por_preventa = (
                df_banner.groupby(col_preventa)["id_visit"]
                .nunique()
                .reset_index(name="Total")
            )

            finalizadas_por_preventa = (
                df_banner[df_banner["status_visit"] == "Finalizado"]
                .groupby(col_preventa)["id_visit"]
                .nunique()
                .reset_index(name="Finalizadas")
            )

            # --- Unir y calcular % de ejecución ---
            ejecucion = pd.merge(total_por_preventa, finalizadas_por_preventa, on=col_preventa, how="left").fillna(0)
            ejecucion["% Ejecución"] = (ejecucion["Finalizadas"] / ejecucion["Total"]) * 100
            ejecucion = ejecucion.sort_values("% Ejecución", ascending=True)

            # --- Gráfico horizontal con Altair ---
            bars = alt.Chart(ejecucion).mark_bar(
                color="#666666",  # azul corporativo
                cornerRadiusTopRight=3,
                cornerRadiusBottomRight=3
            ).encode(
                y=alt.Y(f"{col_preventa}:N", sort='-x', title="Usuario"),
                x=alt.X("% Ejecución:Q", title="% Ejecución", scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip(f"{col_preventa}:N", title="Usuario"),
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
                title="% de Ejecución por Usuario",
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
            st.altair_chart(grafico_ejecucion_por_preventa(df_filtrado_banner), use_container_width=True)







    with col2:


        def chart_dona(df, variable, question_id=None, titulo="", etiqueta="", colores=None):
            # Si se pasa question_id, se filtra por esa pregunta
            if question_id is not None:
                df_plot = (
                    df[df["question_id_answer"] == question_id]
                    .groupby("answer_answer")["visit_id_answer"]
                    .nunique()
                    .reset_index()
                    .rename(columns={"visit_id_answer": "total", "answer_answer": etiqueta})
                )
            else:
                # Caso cuando no hay question_id (por ejemplo status_visit)
                df_plot = (
                    df.groupby(variable)["visit_id_answer"]
                    .nunique()
                    .reset_index()
                    .rename(columns={"visit_id_answer": "total", variable: etiqueta})
                )

            # Calcular porcentajes
            df_plot["porcentaje"] = (df_plot["total"] / df_plot["total"].sum() * 100).round(1)

            # Colores por defecto si no se pasan
            if colores is None:
                colores = ["#AF0E0E", "#888888", "#CCCCCC"]

            # Crear el gráfico tipo dona
            chart = (
                alt.Chart(df_plot)
                .mark_arc(innerRadius=40)  # 🎯 innerRadius crea efecto de dona
                .encode(
                    theta=alt.Theta("total:Q"),
                    color=alt.Color(
                        f"{etiqueta}:N",
                        scale=alt.Scale(range=colores),
                        legend=alt.Legend(title=etiqueta),
                    ),
                    tooltip=[
                        alt.Tooltip(f"{etiqueta}:N", title=etiqueta),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%"),
                    ],
                )
                .properties(
                    width=300,
                    height=200,
                    title=titulo,
                    background="transparent",
                )
                .configure_title(
                    fontSize=22,
                    fontWeight="bold",
                    anchor="start",
                    color="#000000",
                )
                .configure_legend(
                    labelColor="#000000",
                    titleColor="#000000",
                    labelFontSize=13,
                    titleFontSize=14,
                )
            )

            return chart
        

        with st.container(border=True):
            st.altair_chart(
                chart_dona(df_filtrado_banner, "answer_answer", 5, "Incidencias", "Motivo", ["#FF0000", "#666666", "#6B1F1F",  "#EE8787", "#000000", "#DC0707",  "#490707",  "#4C4A4A",  "#CA4545", "#BA0000"]),
                use_container_width=True
            )

        with st.container(border=True):
            st.altair_chart(
                chart_dona(df_filtrado_banner, "answer_answer", 14, "Tamaños", "Tamaño", [ "#FF0000", "#666666", "#6B1F1F",  "#EE8787", "#000000", "#DC0707",  "#490707",  "#4C4A4A",  "#CA4545", "#BA0000"]),
                use_container_width=True
            )

        with st.container(border=True):
            st.altair_chart(
                chart_dona(df_filtrado_banner, "answer_answer", 17, "Posición", "Posición", [ "#FF0000", "#666666", "#6B1F1F",  "#EE8787", "#000000", "#DC0707",  "#490707",  "#4C4A4A",  "#CA4545", "#BA0000"]),
                use_container_width=True
            )

        with st.container(border=True):
            st.altair_chart(
                chart_dona(df_filtrado_banner, "status_visit", None, "Estado de Finalización", "Estado", ["#A71616", "#666666", "#CCCCCC"]),
                use_container_width=True
            )



