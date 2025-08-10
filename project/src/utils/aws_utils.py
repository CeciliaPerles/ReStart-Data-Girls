import logging

import boto3
import os
import io
import pandas as pd

def put_file_s3(source_path: str, destination_path: str, source_type: str, file_format: str):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('REGION_NAME')
    )
    if source_type == 'file':
        with open(source_path, 'rb') as f:
            s3.put_object(Bucket=os.getenv('BUCKET'), Key=destination_path, Body=f)

    elif source_type == 's3':
        df = get_object_s3(source_path, file_format)
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        s3.put_object(Bucket=os.getenv('BUCKET'), Key=destination_path, Body=buffer)

    else:
        logging.error(f"Source type {source_type} não suportado.")
        raise ValueError('Source type precisa ser file ou s3.')


def put_df_s3(df:pd.DataFrame, destination_path: str, file_format: str):

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('REGION_NAME')
    )
    buffer = io.BytesIO()

    if file_format == 'csv':
        df.to_csv(buffer, index=False)

    elif file_format == 'parquet':
        df.to_parquet(buffer, index=False)

    else:
        logging.error(f"File format {file_format} não suportado.")
        raise ValueError('File format precisa ser csv ou parquet.')

    buffer.seek(0)
    s3.put_object(Bucket=os.getenv('BUCKET'), Key=destination_path, Body=buffer)

def get_object_s3(source_path: str, format: str) -> pd.DataFrame:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('REGION_NAME')
    )

    object = s3.get_object(Bucket=os.getenv('BUCKET'), Key=source_path)
    if format == 'csv':
        return pd.read_csv(io.BytesIO(object['Body'].read()))
    elif format == 'parquet':
        return pd.read_parquet(io.BytesIO(object['Body'].read()))
    else:
        raise ValueError('Invalid format')