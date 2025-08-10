import pandas as pd
import logging
import re
import os
import datetime
from src.utils.aws_utils import put_file_s3, get_object_s3, put_df_s3

def rename_columns_snake_case(df: pd.DataFrame) -> pd.DataFrame:
    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Entrada deve ser um DataFrame")

        df.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', col).lower() for col in df.columns]
        return df

    except Exception as e:
        logging.error(f"Falha ao renomear colunas para snake_case: {e}")
        return df

def rename_columns_ptbr(dict_df: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    try:
        col_map = {
            "age": "idade",
            "attrition": "desligado",
            "business_travel": "viagem_a_trabalho",
            "department": "departamento",
            "distance_from_home": "distancia_de_casa",
            "education": "escolaridade",
            "education_field": "area_de_formacao",
            "environment_satisfaction": "satisfacao_com_ambiente",
            "gender": "genero",
            "job_involvement": "engajamento_no_trabalho",
            "job_level": "nivel_do_cargo",
            "job_role": "cargo",
            "job_satisfaction": "satisfacao_no_trabalho",
            "marital_status": "estado_civil",
            "monthly_income": "renda_mensal",
            "num_companies_worked": "num_empregos_anteriores",
            "over_time": "horas_extras",
            "percent_salary_hike": "aumento_percentual_salario",
            "performance_rating": "avaliacao_de_desempenho",
            "relationship_satisfaction": "satisfacao_com_relacoes",
            "stock_option_level": "nivel_de_opcao_de_acoes",
            "total_working_years": "total_anos_experiencia",
            "training_times_last_year": "treinamentos_ultimo_ano",
            "work_life_balance": "equilibrio_vida_trabalho",
            "years_at_company": "anos_na_empresa",
            "years_in_current_role": "anos_no_cargo_atual",
            "years_since_last_promotion": "anos_desde_ultima_promocao",
            "years_with_curr_manager": "anos_com_mesmo_gerente",
            "employee_count": "quantidade_funcionarios",
            "over18": "maior_de_18_anos",
            "standard_hours": "carga_horaria_padrao",
            "employee_number": "numero_funcionario",
            "daily_rate": "remuneracao_diaria",
            "hourly_rate": "remuneracao_por_hora",
            "monthly_rate": "remuneracao_mensal"
        }

        for key, df in dict_df.items():
            dict_df[key] = df.rename(columns=col_map)
            logging.info(f"Colunas renomeadas no DataFrame '{key}'.")

    except Exception as e:
        logging.error(f"Erro ao renomear colunas nos DataFrames: {e}")

    return dict_df

def convert_to_binary(df: pd.DataFrame, col_name:str, is_abbreviated:bool) -> pd.DataFrame:
    try:
        if col_name not in df.columns:
            raise KeyError(f"Coluna {col_name} não encontrada no DataFrame.")

        if is_abbreviated:
            df[col_name] = df[col_name].map({"Y": 1, "N": 0})
        else:
            df[col_name] = df[col_name].map({"Yes": 1, "No": 0})

        if df[col_name].isnull().any():
            logging.warning(f"Valores desconhecidos encontrados na coluna {col_name}.")

        return df

    except Exception as e:
        logging.error(f"Erro ao converter 'attrition' para binário: {e}")
        return df


def translate_categorical_columns(df) -> pd.DataFrame:
    try:
        translations = {
            "business_travel": {
                "Non-Travel": "Não viaja",
                "Travel_Frequently": "Viaja frequentemente",
                "Travel_Rarely": "Viaja raramente"
            },
            "department": {
                "Human Resources": "Recursos Humanos",
                "Research & Development": "Pesquisa e Desenvolvimento",
                "Sales": "Vendas"
            },
            "education_field": {
                "Human Resources": "Recursos Humanos",
                "Life Sciences": "Ciências Biológicas",
                "Marketing": "Marketing",
                "Medical": "Medicina",
                "Other": "Outros",
                "Technical Degree": "Área Técnica"
            },
            "gender": {
                "Male": "Masculino",
                "Female": "Feminino"
            },
            "job_role": {
                "Healthcare Representative": "Representante de Saúde",
                "Human Resources": "Recursos Humanos",
                "Laboratory Technician": "Técnico de Laboratório",
                "Manager": "Gerente",
                "Manufacturing Director": "Diretor de Produção",
                "Research Director": "Diretor de Pesquisa",
                "Research Scientist": "Cientista de Pesquisa",
                "Sales Executive": "Executivo de Vendas",
                "Sales Representative": "Representante de Vendas"
            },
            "marital_status": {
                "Divorced": "Divorciado",
                "Married": "Casado",
                "Single": "Solteiro"
            }
        }

        for col, mapping in translations.items():
            if col in df.columns:
                df[col] = df[col].map(mapping)
                logging.info(f"Coluna '{col}' traduzida com sucesso.")
            else:
                logging.warning(f"Coluna '{col}' não encontrada no DataFrame.")

    except Exception as e:
        logging.error(f"Erro ao traduzir colunas categóricas: {e}")

    return df


def extract_domain_dataframes(df: pd.DataFrame) -> dict[str, pd.DataFrame]:

    try:
        dados_pessoais = [
                "employee_number",
                "age",
                "gender",
                "marital_status",
                "distance_from_home",
                "education",
                "education_field",
            ]

        dados_profissionais = [
                "employee_number",
                "department",
                "job_role",
                "job_level",
                "business_travel",
                "over_time",
                "num_companies_worked",
                "total_working_years",
                "years_at_company",
                "years_in_current_role",
                "years_since_last_promotion",
                "years_with_curr_manager",
                "attrition",
                "performance_rating",
                "percent_salary_hike",
                "training_times_last_year"
            ]

        dados_performance = [
                "employee_number",
                "job_satisfaction",
                "environment_satisfaction",
                "relationship_satisfaction",
                "work_life_balance",
                "job_involvement",
                "monthly_income",
                "daily_rate",
                "hourly_rate",
                "monthly_rate",
                "standard_hours",
                "stock_option_level"
            ]

        personal_df = df[dados_pessoais].copy()
        work_df = df[dados_profissionais].copy()
        performance_df = df[dados_performance].copy()

        logging.info("Domain DataFrames extracted successfully.")
        return {
            "dados_pessoais": personal_df,
            "dados_profissionais": work_df,
            "dados_performance": performance_df
        }

    except KeyError as e:
        logging.error(f"Missing column(s) during domain extraction: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during domain extraction: {e}")

    return {}

def convert_columns_to_binary(df: pd.DataFrame) -> pd.DataFrame:
    df = convert_to_binary(df, "attrition", False)
    df = convert_to_binary(df, "over_time", False)
    return df

def transform_data(key: str) -> dict[str, pd.DataFrame]:

    try:
        logging.info("Iniciando transformações nos dados...")

        df = get_object_s3(key, "csv")
        df = rename_columns_snake_case(df)
        df = convert_columns_to_binary(df)
        df = translate_categorical_columns(df)
        dict_df_domains = extract_domain_dataframes(df)
        dict_df_domains = rename_columns_ptbr(dict_df_domains)

        for name, df_domain in dict_df_domains.items():
            transform_dir = os.path.join("data", "transform")
            os.makedirs(transform_dir, exist_ok=True)

            file_path = os.path.join(transform_dir, f"{name}.parquet")
            df_domain.to_parquet(file_path, index=False)

            put_df_s3(
                df_domain,
                f"transform/{datetime.date.today()}/{name}.parquet",
                'parquet'
            )

        logging.info("Transformações concluídas com sucesso.")
        return dict_df_domains

    except Exception as e:
        logging.error(f"Erro durante transformações: {e}")
        raise e