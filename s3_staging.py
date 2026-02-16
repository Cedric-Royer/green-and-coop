"""
Pipeline de Staging : S3 vers S3.
Ce module extrait les données brutes Airbyte du dossier source, applique les 
transformations de normalisation et sauvegarde les fichiers nettoyés sur S3.
"""

import json
from io import StringIO
from typing import List, Dict, Any

import boto3
import pandas as pd
from dotenv import load_dotenv

from data_transformer import clean_document

# Configuration de l'environnement
load_dotenv()

BUCKET_NAME = 'green-and-coop'
SOURCE_FOLDER = 'stations-source-data/'
DEST_FOLDER = 'ready_for_mongo/'

s3_client = boto3.client('s3')

def process_and_prepare_s3() -> None:
    """
    Orchestre le cycle ETL (Extract, Transform, Load) pour le stockage S3.
    """
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=SOURCE_FOLDER)
    
    if 'Contents' not in response:
        print("Information : Aucun objet détecté dans le préfixe source.")
        return

    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        
        # Filtre les fichiers valides
        if not s3_key.lower().endswith(('.csv', '.csv.csv')):
            continue
            
        print(f"Processing object: {s3_key}")
        
        try:
            # Extraction des données brutes
            raw_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
            df_raw = pd.read_csv(raw_obj['Body'])
            
            if '_airbyte_data' not in df_raw.columns:
                continue
                
            # Transformation des données
            raw_rows: List[Dict[str, Any]] = [json.loads(row) for row in df_raw['_airbyte_data']]
            final_rows: List[Dict[str, Any]] = []

            for row in raw_rows:
                # Normalisation des structures imbriquées (Format Nord_FR)
                if 'stations' in row and isinstance(row['stations'], list):
                    for station in row['stations']:
                        combined_data = {
                            **station,
                            "metadata": row.get("metadata"),
                            "hourly": row.get("hourly")
                        }
                        final_rows.append(clean_document(combined_data))
                else:
                    # Format standard (Ichtegem, La Madeleine)
                    final_rows.append(clean_document(row))
            
            # Préparation du fichier de sortie
            df_final = pd.DataFrame(final_rows)

            folder_name = s3_key.split('/')[1]

            # Source_File_Stations_Nord_FR/
            if folder_name.startswith('Source_File_'):
                site_id = folder_name.replace('Source_File_', '')
            # Ichtegem_BE_source_file / La_Madeleine_FR_source_file
            elif folder_name.endswith('_source_file'):
                site_id = folder_name.replace('_source_file', '')
            # Fallback
            else:
                site_id = folder_name

            output_key = f"{DEST_FOLDER}{site_id}_clean.csv"
            
            # Chargement vers la destination S3
            csv_buffer = StringIO()
            df_final.to_csv(csv_buffer, index=False)
            s3_client.put_object(
                Bucket=BUCKET_NAME, 
                Key=output_key, 
                Body=csv_buffer.getvalue()
            )
            
            print(f"Success: {output_key} | Count: {len(final_rows)}")

        except Exception as e:
            print(f"Critical error processing {s3_key}: {e}")

if __name__ == "__main__":
    process_and_prepare_s3()