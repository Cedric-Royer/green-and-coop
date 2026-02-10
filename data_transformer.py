from utils.converters import fahrenheit_to_celsius, extract_numeric

def clean_document(doc):
    """
    Normalisation métier du document.
    S'appuie sur les utilitaires de conversion pour le Clean Code.
    """
    mapping = {
        'Temperature': 'temperature',
        'Dew Point': 'dew_point',
        'Humidity': 'humidity',
        'Pressure': 'pressure',
        'Precip. Accum.': 'precip_accum',
        'Precip. Rate.': 'precip_rate',
        'Wind': 'wind_direction',
        'Speed': 'wind_speed',
        'Gust': 'wind_gust',
        'Solar': 'solar_radiation',
        'UV': 'uv_index',
        'Time': 'timestamp'
    }
    
    normalized = {}
    for key, value in doc.items():
        new_key = mapping.get(key, key.lower().replace(' ', '_'))
        
        # Logique : Si c'est un champ de température en Fahrenheit, on convertit.
        # Sinon, on extrait juste le nombre.
        is_temp = any(x in new_key for x in ['temperature', 'dew_point'])
        is_f = isinstance(value, str) and '°F' in value
        
        if is_temp and is_f:
            normalized[new_key] = fahrenheit_to_celsius(value)
        else:
            normalized[new_key] = extract_numeric(value)
            
    return normalized