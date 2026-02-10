import re

def fahrenheit_to_celsius(value):
    """
    Formule de conversion pure : (F - 32) * 5/9.
    Supporte les floats ou les strings contenant '°F'.
    """
    numeric_value = None
    
    if isinstance(value, (int, float)):
        numeric_value = float(value)
    elif isinstance(value, str):
        match = re.search(r"([-+]?\d*\.\d+|\d+)", value)
        if match:
            numeric_value = float(match.group(1))
    
    if numeric_value is not None:
        c_val = (numeric_value - 32) * 5 / 9
        return round(c_val, 1)
    
    return value

def extract_numeric(value):
    """
    Extrait simplement le nombre d'une chaîne (ex: '4.4 mph' -> 4.4).
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"([-+]?\d*\.\d+|\d+)", value)
        if match:
            return float(match.group(1))
    return value