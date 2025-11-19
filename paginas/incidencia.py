import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt
import pandas as pd
import base64
from pathlib import Path

def load_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def mostrar_incidencia(df_filtrado):
    st.title("Incidencias")


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
 


    
    # --- KPIs ---
    df_filtrado = df_filtrado.copy()
    df_filtrado_incidencias = df_filtrado[df_filtrado["sectionid_answer"].isin([2,5])]
    incidencias_lona = df_filtrado_incidencias[df_filtrado_incidencias["id_section"].isin([2])]["visit_id_answer"].nunique()
    incidencias_banner = df_filtrado_incidencias[df_filtrado_incidencias["id_section"].isin([5])]["visit_id_answer"].nunique()
    fotos = df_filtrado_incidencias[df_filtrado_incidencias["answer_answer"].astype(str).str.contains(".jpg", na=False)]["visit_id_answer"].count()
    VisitasConComentario = ( df_filtrado_incidencias[ (df_filtrado_incidencias["question_id_answer"].isin([7, 10])) & (df_filtrado_incidencias["answer_answer"].notna()) & (df_filtrado_incidencias["answer_answer"] != "") ]["visit_id_answer"] .nunique())


    # Fila superior con KPIs + filtro
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1.2])

    with col1:
        kpi_card("Incidencias Lona", f"{incidencias_lona:,}", icon="imagenes/lona.png")
    with col2:
        kpi_card("Incidencias Banner + Rack", f"{incidencias_banner:,}", icon="imagenes/diseno-de-banner.png")
    with col3:
        kpi_card("Fotos", f"{fotos}", icon="imagenes/galeria-de-imagenes (1).png")
    with col4:
        kpi_card("Incidencias con Comentario", f"{VisitasConComentario:,}", icon="imagenes/nuevo-mensaje.png")
    with col5:
        # título encima
        st.markdown(
            "<div style='font-size:12px; font-weight:bold; color:black; text-align:center;'>"
            "Tipo de Incidencia</div>",
            unsafe_allow_html=True
        )

        # preparar opciones
        df_incidencias = df_filtrado_incidencias[
            (df_filtrado_incidencias["question_id_answer"].isin([5, 8])) &
            (~df_filtrado_incidencias["answer_answer"].isna())
        ]
        opciones_incidencia = ["Todas"] + df_incidencias["answer_answer"].unique().tolist()

        # selectbox sin recuadro KPI
        tipo_incidencia = st.selectbox(
            " ",
            opciones_incidencia,
            label_visibility="collapsed",
            key="tipo_incidencia"
        )

        # aplicar filtro
        if tipo_incidencia != "Todas":
            df_filtrado_incidencias = df_filtrado_incidencias[
                df_filtrado_incidencias["answer_answer"] == tipo_incidencia
            ]

        df_filtrado_incidencias["ended_at_visit"] = pd.to_datetime(df_filtrado_incidencias["ended_at_visit"])
        df_filtrado_incidencias["ended_date"] = df_filtrado_incidencias["ended_at_visit"].dt.date

        df_filtrado["ended_at_visit"] = pd.to_datetime(df_filtrado["ended_at_visit"])
        df_filtrado["ended_date"] = df_filtrado["ended_at_visit"].dt.date

            # --- Calcular incidencias ---
    incidencias = (
        df_filtrado_incidencias[df_filtrado_incidencias["id_section"].isin([2,5])]
        .groupby("ended_date")["visit_id_answer"].nunique()
        .reset_index(name="Incidencias")
        )

        # --- Calcular finalizadas ---
    finalizadas = (
        df_filtrado[df_filtrado["status_visit"] == "Finalizado"]
        .groupby("ended_date")["visit_id_answer"].nunique()
        .reset_index(name="Finalizadas")
        )

    # --- Tabla matriz de Incidencias ---
    # Visitas Únicas
    tabla = df_filtrado_incidencias.drop_duplicates(subset=["visit_id_answer"])[[
                "visit_id_answer",
                "store_sap_store",
                "store_name_store",
                "store_zone_store",
                "store_region_store",
                "name_type",
                "FechaHora_Menos6h_visit",
                "status_visit",
                "name_provider"

        ]]

    prueba_fot = df_filtrado_incidencias.loc[df_filtrado_incidencias["question_id_answer"].isin([6,9]), ["visit_id_answer", "answer_answer"]].dropna(subset=["answer_answer"])
    prueba_fot = prueba_fot.groupby("visit_id_answer")["answer_answer"].max().reset_index()
    prueba_fot.rename(columns={"answer_answer": "Prueba_fotografica"}, inplace=True)

    tabla = tabla.merge(prueba_fot[["visit_id_answer", "Prueba_fotografica"]], 
                            on="visit_id_answer", 
                            how="left")

    prueba_incidencia = (
            df_filtrado_incidencias[df_filtrado_incidencias["id_section"].isin([2, 5])]
            .loc[:, ["visit_id_answer", "id_section"]]
            .dropna(subset=["id_section"])
        )

    prueba_incidencia["Incidencia"] = prueba_incidencia["id_section"].map({
            2: "Lona",
            5: "Banner + Rack"
        })

    prueba_incidencia = (
            prueba_incidencia.groupby("visit_id_answer")["Incidencia"].first().reset_index()
        )

    tabla = tabla.merge(prueba_incidencia[["visit_id_answer", "Incidencia"]], 
                            on="visit_id_answer", 
                            how="left")


    comentario = df_filtrado_incidencias[df_filtrado_incidencias["question_id_answer"].isin([7, 10])]
    comentario = comentario.groupby("visit_id_answer")["answer_answer"].first().reset_index(name = "comentario")

    tabla = tabla.merge(comentario,
                            on="visit_id_answer",
                            how = "left")
        
    motivo = df_filtrado_incidencias[df_filtrado_incidencias["question_id_answer"].isin([5, 8])]
    motivo = motivo.groupby("visit_id_answer")["answer_answer"].first().reset_index(name = "motivo")

    tabla = tabla.merge(motivo,
                            on="visit_id_answer",
                            how = "left")
    
    tabla["Tiene Comentario"] = tabla["comentario"].apply(
    lambda x: "Sí" if pd.notna(x) and str(x).strip() != "" else "No"
)

    tabla_final = tabla[[
            "Prueba_fotografica",
            "Incidencia",
            "FechaHora_Menos6h_visit",
            "store_zone_store",
            "store_region_store",
            "name_provider",
            "store_name_store",
            "store_sap_store",
            "motivo",
            "comentario",
            "Tiene Comentario"
        ]]

        # --- Seleccionar y renombrar columnas finales ---
    tabla_final.rename(columns={
            "Prueba_fotografica" : "PRUEBA FOTOGRÁFICA",
            "Incidencia": "INCIDENCIA",
            "FechaHora_Menos6h_visit": "FECHA VISITA",
            "store_zone_store": "ZONA",
            "store_region_store": "REGION",
            "name_provider": "PROVEEDOR",
            "store_name_store": "PDV",
            "store_sap_store": "SAP",
            "motivo": "MOTIVO",
            "comentario": "COMENTARIO",
            "Tiene Comentario": "TIENE COMENTARIO"
        }, inplace=True)


    col1, col2 = st.columns([5, 3])  # tabla grande a la izquierda, gráficos a la derecha

    with col1:

        # --- Unir ambos ---
        resumen = pd.merge(incidencias, finalizadas, on="ended_date", how="outer").fillna(0)

        fig = go.Figure()

        # Barras de incidencias
        fig.add_trace(go.Bar(
            x=resumen["ended_date"],
            y=resumen["Incidencias"],
            name="Incidencias",
            marker=dict(
                color="#AF0E0E",
                line=dict(width=0)
            ),
            text=resumen["Incidencias"],
            textposition="outside",
            textfont=dict(color="black", size=12)  # etiquetas negras
        ))

        # Línea de finalizadas
        fig.add_trace(go.Scatter(
            x=resumen["ended_date"],
            y=resumen["Finalizadas"],
            name="Finalizadas",
            mode="lines+markers+text",
            line=dict(color="#511818", width=2),
            text=resumen["Finalizadas"],
            textposition="top center",
            textfont=dict(color="black", size=12)
        ))

        # --- Estilo general ---
        fig.update_layout(
            title=dict(
                text="<b>Finalizadas vs Incidencias</b>",  # negrita
                font=dict(size=22, color="black"),          # estilo del título
                x=0,                                        # alineado a la izquierda
                xanchor="left",
                y=0.95,
                yanchor="top"
            ),
            xaxis_title="Fecha",
            yaxis_title="Cantidad",
            barmode="group",
            legend=dict(
                orientation="h",
                y=-0.25,
                x=0.3,
                font=dict(color="black")
            ),
            template="plotly_white",                        # base blanca pero transparente
            paper_bgcolor="rgba(0,0,0,0)",                  # fondo total transparente
            plot_bgcolor="rgba(0,0,0,0)",                   # fondo del área de trazado transparente
            height=350
        )
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)

                # título encima
        st.markdown(
            "<div style='font-size:12px; font-weight:bold; color:black; text-align:center;'>"
            "Tiene Comentario</div>",
            unsafe_allow_html=True
        )


        opciones_incidencia = ["Todas"] + tabla_final["TIENE COMENTARIO"].unique().tolist()

        # selectbox sin recuadro KPI
        tiene_comentario = st.selectbox(
            " ",
            opciones_incidencia,
            label_visibility="collapsed",
            key="tiene_comentario"
        )

        # aplicar filtro
        if tiene_comentario != "Todas":
            tabla_final = tabla_final[
                tabla_final["TIENE COMENTARIO"] ==  tiene_comentario
            ]

    with col2:

        def chart_incidencias_lona_banner(df_filtrado, incidencias_lona, incidencias_banner):

            total_visitas = df_filtrado["visit_id_answer"].nunique()

            # 🔹 Visitas con incidencias (lona + banner)
            total_incidencias = incidencias_lona + incidencias_banner

            # 🔹 Visitas sin incidencias
            sin_incidencias = total_visitas - total_incidencias
            if sin_incidencias < 0:
                sin_incidencias = 0   # por segurida

            # Crear dataframe con los valores
            data = pd.DataFrame({
                "Incidencia": ["Lona", "Banner + Rack", "Sin Incidencias"],
                "total": [incidencias_lona, incidencias_banner, sin_incidencias]
            })

            # Calcular porcentaje
            data["porcentaje"] = (data["total"] / data["total"].sum() * 100).round(1)

            # Colores personalizados
            colores = ["#FF0000", "#666666", "#6B1F1F"]  # verde para “sin incidencias”

            # Pie chart
            pie = (
                alt.Chart(data)
                .mark_arc()
                .encode(
                    theta=alt.Theta("total:Q"),
                    color=alt.Color(
                        "Incidencia:N",
                        scale=alt.Scale(range=colores),
                        legend=alt.Legend(title="Tipo de Incidencia")
                    ),
                    tooltip=[
                        alt.Tooltip("Incidencia:N", title="Tipo"),
                        alt.Tooltip("total:Q", title="Total"),
                        alt.Tooltip("porcentaje:Q", format=".1f", title="%")
                    ]
                )
            )

            chart = (
                pie.properties(
                    width=300,
                    height=200,
                    title="Incidencias",
                    background="transparent" )

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


        def chart_incidencias(df_final):
            # Filtrar incidencias (question_id = 8)
            df_inc = (
                df_final[df_final["question_id_answer"].isin([5,8])]
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
                        height=200,
                        title="Tipología de Incidencias",
                        background="transparent" )

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
            st.altair_chart(chart_incidencias_lona_banner(df_filtrado,incidencias_lona, incidencias_banner), use_container_width=True)
        with st.container(border=True):
            st.altair_chart(chart_incidencias(df_filtrado_incidencias), use_container_width=True)




        # Aplicar estilo para aumentar altura de filas
    styled_df = tabla_final.style.set_properties(**{
            'height': '200px',  # alto de la fila
            'line-height': '50px'  # también ajusta el texto vertical
        })


        # Mostrar tu tabla
    with st.container(border=True):
        st.markdown("### Tabla de Total de Incidencias")
        st.dataframe(
                styled_df,
                column_config={
                    "PRUEBA FOTOGRÁFICA": st.column_config.ImageColumn("PRUEBA FOTOGRÁFICA", width="small", )
                },
                use_container_width=True, height=500
            )

