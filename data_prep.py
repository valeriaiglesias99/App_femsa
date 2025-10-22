# data_prep.py
import pandas as pd

def load_data():
    import pandas as pd

    stores = pd.read_csv("datos/stores.csv")
    providers = pd.read_csv("datos/providers1.csv")
    visits = pd.read_csv("datos/visits_1.csv")
    answer = pd.read_csv("datos/answer.csv")
    types = pd.read_csv("datos/types.csv")

    # Renombrar columnas con sufijo por tabla
    stores = stores.add_suffix("_store")
    providers = providers.add_suffix("_provider")
    visits = visits.add_suffix("_visit")
    answer = answer.add_suffix("_answer")
    type = types.add_suffix("_type")

    # Unir tablas
    df_final = visits.merge(
        answer, left_on="id_visit", right_on="visit_id_answer", how="left"
    )
    df_final = df_final.merge(
        stores, left_on="store_id_visit", right_on="id_store", how="left"
    )
    df_final = df_final.merge(
        providers, left_on="user_id_visit", right_on="id_user_provider", how="left"
    )

    df_final = df_final.merge(
        type, left_on="type_id_visit", right_on="id_type", how="left"
    )

    df_final["Periodo_visit"] = df_final["Periodo_visit"].astype(str).replace("Periodo 1", "Periodo 5")


    return df_final