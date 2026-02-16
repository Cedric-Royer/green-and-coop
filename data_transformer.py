import pandas as pd
from utils.converters import fahrenheit_to_celsius, extract_numeric

def clean_document(doc):
    """
    Normalise un document météo : concaténation de la date, conversion 
    des unités et nettoyage des types de données.
    """
    # 1. Exclusion des formats complexes déjà structurés (Nord_FR)
    if 'hourly' in doc or 'station_details' in doc:
        return doc
    
    # 2. Extraction et formatage de la date (Source: DDMMYY / Time: HH:MM:SS)
    raw_date = str(doc.get('Date', doc.get('date', ''))).strip().split('.')[0].zfill(6)
    raw_time = str(doc.get('Time', doc.get('time', '00:00:00'))).strip()
    
    if len(raw_date) == 6:
        day, month, year = raw_date[0:2], raw_date[2:4], raw_date[4:6]
        time_part = f"00:{raw_time.zfill(2)}:00" if ":" not in raw_time else raw_time
        dh_utc_final = f"20{year}-{month}-{day} {time_part}"
    else:
        # Fallback sur les champs existants ou date par défaut
        dh_utc_final = doc.get('src_dh_utc', doc.get('dh_utc', "1970-01-01 00:00:00"))

    # 3. Définition du mapping des colonnes cibles
    mapping = {
        'Temperature': 'temperature', 'Dew Point': 'dew_point',
        'Humidity': 'humidity', 'Pressure': 'pressure',
        'Precip. Accum.': 'precip_accum', 'Precip. Rate.': 'precip_rate',
        'Wind': 'wind_direction', 'Speed': 'wind_speed',
        'Gust': 'wind_gust', 'Solar': 'solar_radiation', 'UV': 'uv_index'
    }

    normalized = {'dh_utc': dh_utc_final}

    # 4. Boucle de nettoyage et conversion des valeurs
    for key, value in doc.items():
        lk = key.lower()
        
        # Ignorer les clés sources de date et les métadonnées techniques
        if lk in ['date', 'time', 'dh_utc', 'src_dh_utc'] or 'airbyte' in lk or lk == '_id':
            continue
            
        new_key = mapping.get(key, lk.replace(' ', '_'))
        
        # Conversion spécifique des températures en Fahrenheit
        if any(x in new_key for x in ['temperature', 'dew_point']) and '°F' in str(value):
            normalized[new_key] = fahrenheit_to_celsius(value)
        else:
            # Nettoyage numérique (suppression des unités et conversion float)
            normalized[new_key] = extract_numeric(value)
            
    return normalized