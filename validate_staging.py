import pandas as pd
import boto3
from io import BytesIO
import ast

BUCKET_NAME = 'green-and-coop'
PREFIX = 'ready_for_mongo/'
s3 = boto3.client('s3')

def check_data_integrity():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    if 'Contents' not in response:
        return

    for obj in response['Contents']:
        key = obj['Key']
        if not key.endswith('_clean.csv'):
            continue
            
        resp = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        df = pd.read_csv(BytesIO(resp['Body'].read()))
        if df.empty:
            continue

        # CAS 1 : Stations_Nord_FR (Structure avec objets imbriqués)
        if "Stations_Nord_FR" in key:
            # On vérifie que les colonnes complexes existent
            for col in ['hourly', 'metadata']:
                if col not in df.columns:
                    raise ValueError(f"Colonne {col} manquante dans {key}")
            
            print(f"Validation Structure Complexe OK: {key}")

        # CAS 2 : Les autres (Ichtegem, La Madeleine, etc. - Structure à plat)
        else:
            if 'dh_utc' not in df.columns:
                raise ValueError(f"dh_utc manquant dans {key}")
            
            if not str(df.iloc[0]['dh_utc']).startswith('2024-'):
                raise ValueError(f"Format date incorrect dans {key}: {df.iloc[0]['dh_utc']}")

        # Commun aux deux : Sécurité Airbyte
        forbidden = ['_airbyte_data', '_airbyte_ab_id']
        if any(col in df.columns for col in forbidden):
            raise ValueError(f"Champs Airbyte résiduels dans {key}")

if __name__ == "__main__":
    check_data_integrity()
    print("VALIDATION SUCCESS")