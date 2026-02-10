# GreenAndCoop : Pipeline Forecast 2.0 (Staging S3)

Ce module constitue la brique de **Transformation** (T) du pipeline ETL de GreenAndCoop. Il assure le passage des données brutes (extraites via Airbyte) vers un format normalisé, prêt à être ingéré dans la base de données MongoDB pour les modèles de prévision de charge électrique des Data Scientists.

---

## 📋 Contexte du projet

Dans le cadre du projet **Forecast 2.0**, nous intégrons des sources météo hétérogènes (InfoClimat, Weather Underground) pour affiner les prévisions de consommation dans les Hauts-de-France.

Ce module automatise la normalisation des relevés météo qui arrivent avec des structures JSON imbriquées et des unités disparates (ex: Fahrenheit).

## ⚙️ Logique de transformation

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

- **Langage :** Python 3.x
- **Infrastructure :** AWS S3 (Stockage objet)
- **Librairies :**
  - `boto3` : Interface avec AWS.
  - `pandas` : Manipulation de données.
  - `python-dotenv` : Gestion des variables d'environnement.

## Installation et utilisation

### 1. Configuration

Créez un fichier `.env` à la racine du projet pour vos accès AWS :

```text
AWS_ACCESS_KEY_ID=votre_cle
AWS_SECRET_ACCESS_KEY=votre_secret
AWS_DEFAULT_REGION=eu-west-
```

### 2. Dépendances

#### Création de l'environnement virtuel

python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

#### Installation des dépendances

pip install -r requirements.txt

### 3. Dépendances

```bash
python s3_staging.py
```
