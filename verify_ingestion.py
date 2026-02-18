import os
from pymongo import MongoClient

def run_check():
    # Configuration interne Docker
    client = MongoClient("mongodb://database:27017/")
    db = client["green_and_coop"]
    col = db["stations_nord_fr"]

    count = col.count_documents({})
    if count == 0:
        raise ValueError("CRITICAL: MongoDB collection is empty after ingestion")
    
    print(f"Check Ingestion: {count} documents found.")

    # Vérification spécifique Nord_FR
    nord_sample = col.find_one({"extraction_source": {"$regex": "Stations_Nord_FR"}})
    if nord_sample and not isinstance(nord_sample.get('hourly'), (dict, list)):
        raise ValueError("CRITICAL: Nord_FR structure is not nested in MongoDB")

if __name__ == "__main__":
    run_check()
    print("VERIFICATION SUCCESS")