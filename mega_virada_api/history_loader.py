import requests
import json
import os
from datetime import datetime

# Source: guilhermeasn/loteria.json (A reliable source for brazilian lottery data)
DATA_URL = "https://raw.githubusercontent.com/guilhermeasn/loteria.json/master/data/megasena.json"
CACHE_FILE = "megasena_history.json"

def fetch_history(force_update=False):
    """
    Fetches the full history of Mega Sena.
    Uses a local cache to avoid spamming the GitHub source.
    """
    if not force_update and os.path.exists(CACHE_FILE):
        # Check if cache is recent (e.g., less than 1 day old)
        file_time = os.path.getmtime(CACHE_FILE)
        if (datetime.now().timestamp() - file_time) < 86400:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)

    # Fetch from web
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        data = response.json()
        
        # Save to cache
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
            
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        # Fallback to cache if available, even if old
        if os.path.exists(CACHE_FILE):
             with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return []

def get_all_draws():
    """
    Returns a standardized list of draws:
    [
      { "concurso": 1, "dezenas": [4, 5, 30, 33, 41, 52] },
      ...
    ]
    """
    raw_data = fetch_history()
    clean_draws = []
    
    # Check if data is dict (Key=Concurso, Value=List of Strings)
    if isinstance(raw_data, dict):
        for concurso_str, dezenas_list in raw_data.items():
            try:
                concurso = int(concurso_str)
                # Convert strings to integers
                dezenas = [int(n) for n in dezenas_list]
                
                clean_draws.append({
                    "concurso": concurso,
                    "dezenas": sorted(dezenas)
                })
            except ValueError:
                continue
                
        # Sort by concurso
        clean_draws.sort(key=lambda x: x['concurso'])
        return clean_draws

    # Fallback for list format (if source changes)
    elif isinstance(raw_data, list):
        for draw in raw_data:
            try:
                numero = draw.get("Concurso")
                dezenas = draw.get("Dezenas", [])
                if dezenas and isinstance(dezenas[0], str):
                    dezenas = [int(n) for n in dezenas]
                clean_draws.append({
                    "concurso": numero,
                    "dezenas": sorted(dezenas)
                })
            except:
                continue
            
    return clean_draws
