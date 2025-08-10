from src.extract.extract import extract_data
from src.transform.transform import transform_data
from src.load.load import load_data
from dotenv import load_dotenv
import logging
import sys


def main():
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    try:
        logging.info("Iniciando pipeline ETL")
        
        extracted_key = extract_data()
        logging.info(f"Planilha extraída com sucesso.")

        transform_data(extracted_key)
        logging.info(f"Planilha transformada com sucesso.")

        load_data()
        logging.info("Pipeline ETL concluído com sucesso")

    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()