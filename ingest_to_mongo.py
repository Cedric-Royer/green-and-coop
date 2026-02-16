import boto3
import pandas as pd
import ast
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = 'green-and-coop'
SOURCE_PREFIX = 'ready_for_mongo/'
MONGO_URI = "mongodb://database:27017/"
DATABASE_NAME = "green_and_coop"
COLLECTION_NAME = "stations_nord_fr"

s3_client = boto3.client('s3')
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

def ingest_station_data(s3_key: str):
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    df = pd.read_csv(response['Body'])

    for col in ['hourly', 'metadata', 'station_details']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    documents = df.to_dict(orient='records')

    if documents:
        for d in documents:
            d['extraction_source'] = s3_key
        db[COLLECTION_NAME].insert_many(documents)
        print(f"OK: {s3_key}")

if __name__ == "__main__":
    db[COLLECTION_NAME].delete_many({})
    
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=SOURCE_PREFIX):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('_clean.csv'):
                ingest_station_data(key)