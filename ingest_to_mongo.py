import boto3
import json
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration des ressources
BUCKET_NAME = 'green-and-coop'
SOURCE_PREFIX = 'stations-source-data/'
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "green_and_coop"

# Initialisation des clients S3 et MongoDB
s3_client = boto3.client('s3')
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

def get_s3_keys(bucket, prefix):
    """
    Identifie dynamiquement les clés d'objets S3 pour éviter les erreurs de saisie manuelle.
    Filtre les fichiers CSV et gère les anomalies de nommage.
    """
    keys = []
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            if obj['Key'].lower().endswith('.csv') or '.csv.csv' in obj['Key'].lower():
                keys.append(obj['Key'])
    return keys

def ingest_station_data(s3_key: str):
    """
    Extrait les données Airbyte, fragmente les listes d'objets (unwind) 
    et injecte les documents BSON dans MongoDB.
    """
    # Normalisation du nom de la collection à partir du chemin S3
    path_segments = s3_key.split('/')
    # On cible le nom du dossier parent (ex: Source_File_Ichtegem_BE)
    folder_name = path_segments[1] if len(path_segments) > 1 else "default"
    collection_name = folder_name.replace('Source_File_', '').lower()
    
    # Lecture de l'objet S3
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    df_raw = pd.read_csv(response['Body'])

    if '_airbyte_data' not in df_raw.columns:
        return

    # Conversion de la colonne sérialisée en dictionnaires Python
    raw_documents = [json.loads(row) for row in df_raw['_airbyte_data']]
    final_documents = []

    for doc in raw_documents:
        # Transformation structurelle : un document par station pour le format Nord_FR
        if 'stations' in doc and isinstance(doc['stations'], list):
            for station in doc['stations']:
                final_documents.append({
                    "station_details": station,
                    "metadata": doc.get('metadata'),
                    "hourly_forecast": doc.get('hourly'),
                    "extraction_source": s3_key
                })
        else:
            # Formatage standard pour les autres sources
            doc['extraction_source'] = s3_key
            final_documents.append(doc)

    if final_documents:
        # Nettoyage de la collection avant insertion pour éviter les doublons
        db[collection_name].delete_many({"extraction_source": s3_key})
        
        # Insertion des documents transformés
        result = db[collection_name].insert_many(final_documents)
        print(f"Collection: {collection_name} | Documents insérés: {len(result.inserted_ids)}")

if __name__ == "__main__":
    # Récupération dynamique des fichiers 
    all_keys = get_s3_keys(BUCKET_NAME, SOURCE_PREFIX)
    
    if not all_keys:
        print("Aucun fichier source détecté sur S3.")
    
    for key in all_keys:
        try:
            ingest_station_data(key)
        except Exception as e:
            print(f"Erreur lors de l'ingestion de {key} : {e}")