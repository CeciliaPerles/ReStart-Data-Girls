import os
import zipfile
import pandas as pd
import kaggle
import logging
import datetime
from src.utils.aws_utils import put_file_s3

def extract_data() -> str:
    try:
        logging.info("Iniciando extração do dataset.")

        kaggle.api.authenticate()

        # Diretório onde os dados serão salvos
        raw_dir = os.path.join("data", "raw")
        os.makedirs(raw_dir, exist_ok=True)

        # Caminho do zip dentro da pasta raw
        zip_file = os.path.join(raw_dir, "ibm-hr-analytics-attrition-dataset.zip")

        # Faz o download se ainda não existir
        if not os.path.exists(zip_file):
            kaggle.api.dataset_download_files(
                "pavansubhasht/ibm-hr-analytics-attrition-dataset",
                path=raw_dir,
                unzip=False
            )

        # Extrai os arquivos na mesma pasta raw
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(raw_dir)

        # Lê o CSV extraído
        csv_path = os.path.join(raw_dir, "WA_Fn-UseC_-HR-Employee-Attrition.csv")
        bucket_key = f'extract/{datetime.date.today()}/extract.csv'
        put_file_s3(csv_path, bucket_key, 'file', 'csv')

        logging.info("Extração concluída com sucesso.")
        return bucket_key

    except Exception as e:
        logging.error(f"Erro ao extrair dados: {e}")
        raise