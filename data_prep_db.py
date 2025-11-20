# data_prep.py
import pandas as pd
from .connection import get_connection 
import numpy as np

#cargar datos desde la base de datos
def load_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def build_dataset():
    # ================= PROVIDERS ====================
    query_providers = "SELECT id, code, name, email, status FROM providers;"
    providers = load_data(query_providers).add_suffix("_provider")

    # ================= USERS ========================
    query_users = """
    SELECT id, username, email, full_name, status, role, provider_id
    FROM users
    WHERE email NOT LIKE '1%'
      AND email NOT LIKE '2%'
      AND email NOT LIKE 'test%';
    """
    users = load_data(query_users).add_suffix("_user")

    # ================= VISITS =======================
    query_visits = """
    SELECT id, status, started_at, ended_at, created_at, updated_at, 
           store_id, user_id, type_id, time_period_id
    FROM visits
    """
    visits = load_data(query_visits)

    # Estados normalizados
    visits['status'] = visits['status'].replace({
        'pending': 'Pendiente',
        'completed': 'Finalizado',
        'progress': 'En progreso'
    })

    # Manejo de fechas
    visits['updated_at'] = pd.to_datetime(visits['updated_at'])
    visits['fecha'] = visits['updated_at'].dt.date
    visits['FechaHora_Menos6h'] = visits['updated_at'] - pd.Timedelta(hours=6)
    visits['Fecha_Menos6h'] = visits['FechaHora_Menos6h'].dt.date

    visits = visits.add_suffix("_visit")

    # ================= ANSWERS ======================
    query_answers = """
    SELECT id, answer, visit_id, question_id
    FROM answers
    """
    answers = load_data(query_answers)

    # Personalización de respuestas
    answers['Personalizado'] = np.where(
        (answers['answer'] == "Cliente Cerrado") & (answers['question_id'] == 8),
        "Cliente Cerrado Lona",
        np.where(
            (answers['answer'] == "Cliente Cerrado") & (answers['question_id'] == 5),
            "Cliente Cerrado Banner + Rack",
            answers['answer']
        )
    )

    answers = answers.rename(columns={
        'answer': 'answer1',
        'Personalizado': 'answer'
    })

    answers = answers[['id', 'answer', 'visit_id', 'question_id']]

    answers['answer'] = np.where(
        answers['answer'].str.contains('Basic', case=False, na=False),
        'Básico', answers['answer']
    )
    answers['answer'] = np.where(
        answers['answer'].str.contains('Extra\s?Large', case=False, na=False, regex=True),
        'Extragrande', answers['answer']
    )
    answers['answer'] = np.where(
        answers['answer'].str.contains('Large', case=False, na=False),
        'Grande', answers['answer']
    )
    answers['answer'] = answers['answer'].replace(
        'Cliente no tiene Lona',
        'Cliente no tiene Banner'
    )

    answer = answers.add_suffix("_answer")

    # ================= TAMAÑO ASIGNADO ==============

    # Extraer tamaños por visita
    temp = answer[answer["question_id_answer"].isin([4, 14])][
        ["visit_id_answer", "answer_answer"]
    ].rename(columns={
        "visit_id_answer": "id_visit",
        "answer_answer": "TamañoAsignado_answer"
    })

    # Unirlo a visits
    visits = visits.merge(temp, on="id_visit", how="left")

    # ================= TIME PERIODS =================
    query_periods = "SELECT id, name FROM time_periods"
    periods = load_data(query_periods).add_suffix("_period")

    # ================= STORES =======================
    query_stores = """
    SELECT id, store_sap, store_name, store_zone, store_region, store_mr, status
    FROM stores
    """
    stores = load_data(query_stores).add_suffix("_store")

    # ================= QUESTIONS ====================
    query_questions = """
    SELECT id, question, section_id
    FROM questions
    """
    questions = load_data(query_questions).add_suffix("_question")

    # ================= SECTIONS =====================
    query_sections = """
    SELECT id, section_name, status, type_id
    FROM sections
    """
    sections = load_data(query_sections).add_suffix("_section")

    # ================= TYPES ========================
    query_types = """
    SELECT id, name, status
    FROM types
    """
    types = load_data(query_types).add_suffix("_type")

    # ======================================================
    # COMBINAR 
    # ======================================================
    df_combined = providers.merge(
        users, left_on='id_provider', right_on='provider_id_user', how='inner'
    )

    df_combined = df_combined.merge(
        visits, left_on='id_user', right_on='user_id_visit', how='inner'
    )

    df_combined = df_combined.merge(
        periods, left_on='time_period_id_visit', right_on='id_period', how='left'
    )

    df_combined = df_combined.merge(
        answer, left_on='id_visit', right_on='visit_id_answer', how='left'
    )

    df_combined = df_combined.merge(
        stores, left_on='store_id_visit', right_on='id_store', how='inner'
    )

    df_combined = df_combined.merge(
        questions, left_on='question_id_answer', right_on='id_question', how='left'
    )

    df_combined = df_combined.merge(
        sections, left_on='section_id_question', right_on='id_section', how='left'
    )

    df_combined = df_combined.merge(
        types, left_on='type_id_visit', right_on='id_type', how='inner'
    )

    return df_combined