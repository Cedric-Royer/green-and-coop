# GreenAndCoop : Pipeline Forecast 2.0 (Staging S3)

Ce module constitue la brique de **Transformation** (T) du pipeline ETL de GreenAndCoop. Il assure le passage des données brutes (extraites via Airbyte) vers un format normalisé, prêt à être ingéré dans la base de données MongoDB pour les modèles de prévision de charge électrique des Data Scientists.

---

## Contexte du projet

Dans le cadre du projet **Forecast 2.0**, nous intégrons des sources météo hétérogènes (InfoClimat, Weather Underground) pour affiner les prévisions de consommation dans les Hauts-de-France.

Ce module automatise la normalisation des relevés météo qui arrivent avec des structures JSON imbriquées et des unités disparates (ex: Fahrenheit).

## Logique de transformation

Le script réalise les opérations suivantes :

1.  **Extraction :** Scan du bucket S3 `green-and-coop` dans le préfixe `stations-source-data/`.
2.  **Parsing :** Extraction des données brutes contenues dans la colonne `_airbyte_data` (format JSON).
3.  **Normalisation Métier (`clean_document`) :**
    - **Mapping :** Uniformisation des noms de colonnes (ex: `Temperature` -> `temperature`).
    - **Conversions :** Passage automatique des degrés Fahrenheit en Celsius.
    - **Nettoyage :** Extraction des valeurs numériques uniquement (suppression des unités textuelles).
4.  **Gestion des Formats :**
    - Gestion des structures plates (Ichtegem, La Madeleine).
    - Gestion des structures imbriquées (Format Nord_FR) avec explosion des listes de stations.
5.  **Chargement :** Sauvegarde des données nettoyées dans `ready_for_mongo/` au format CSV.

## Stack technique

- **Langage**
  - Python 3.11
- **Infrastructure**
  - AWS S3
  - Docker
  - Docker-Compose
- **Base de données**
  - MongoDB
- **Librairies**
  - `boto3` : Interaction avec le stockage objet S3.
  - `pandas` : Traitement et normalisation des DataFrames.
  - `pymongo` : Ingestion des données vers MongoDB.
  - `python-dotenv` : Gestion des variables d'environnement.

## Installation et utilisation

### 1. Configuration

Créez un fichier `.env` à la racine du projet pour vos accès AWS :

```text
AWS_ACCESS_KEY_ID=votre_cle
AWS_SECRET_ACCESS_KEY=votre_secret
AWS_DEFAULT_REGION=eu-west-
```

### 2. Déploiement Docker

Le pipeline est entièrement conteneurisé. L'orchestration automatise la configuration de la base de données et l'exécution du script d'ingestion.

```bash
docker-compose up --build
```

### Accès Compass

### 3. Visualisation (Compass)

- **Client** : MongoDB Compass
- **URI** : `mongodb://localhost:27018/?directConnection=true`
- **Port Hôte** : 27018
- **Port Conteneur** : 27017

## Schéma du processus ETL

```text
          [ SOURCE S3 : stations-source-data/ ]
                        |
                        v
          [ Extraction S3 vers Pandas ]
                        |
                        v
          [ Parsing & Normalisation ]
           (Airbyte JSON -> DataFrame)
                        |
            +-----------+-----------+
            |                       |
      [ Format Imbriqué ]     [ Format Standard ]
            |                       |
            +----------->+<---------+
                         |
                         v
          [ Stockage S3 : ready_for_mongo/ ]
                         |
                         v
          [ Ingestion : MongoDB (Docker) ]

```

## Format de sortie

Chaque fichier CSV généré contient les champs normalisés suivants :

- **timestamp** : Date et heure de l'observation.
- **temperature** : Température en Celsius (°C).
- **dew_point** : Point de rosée en Celsius (°C).
- **humidity** : Taux d'humidité (%).
- **pressure** : Pression atmosphérique (hPa).
- **wind_speed** : Vitesse du vent (numérique).
- **solar_radiation** : Rayonnement solaire ($W/m^2$).

> **Note :** Tous les champs provenant de sources en Fahrenheit sont automatiquement convertis lors de la phase de transformation. Les unités textuelles (ex: "km/h", "hPa") sont retirées pour ne conserver que la valeur numérique exploitable.

## Exemple de document normalisé

```json
{
  "timestamp": "2024-05-20T14:30:00",
  "temperature": 21.5,
  "humidity": 65,
  "wind_speed": 12.4,
  "status": "cleaned"
}
```
