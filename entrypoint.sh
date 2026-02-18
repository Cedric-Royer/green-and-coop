#!/bin/bash
set -e

echo "--- Étape 1: Staging (S3 to S3) ---"
python s3_staging.py

echo "--- Étape 2: Validation des données ---"
python validate_staging.py

echo "--- Étape 3: Ingestion MongoDB ---"
python ingest_to_mongo.py

echo "--- Étape 4: Vérification finale DB ---"
python verify_ingestion.py

echo "--- Pipeline terminé avec succès ---"