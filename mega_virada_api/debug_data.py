import requests
import json

URL = "https://raw.githubusercontent.com/guilhermeasn/loteria.json/master/data/megasena.json"

try:
    print(f"Fetching from {URL}...")
    r = requests.get(URL)
    data = r.json()
    print("SUCCESS. Data type:", type(data))
    if isinstance(data, dict):
        print("Keys:", data.keys())
        # Print a sample of the first value if it's iterable
        first_key = list(data.keys())[0]
        print(f"Sample of key '{first_key}':", str(data[first_key])[:200])
except Exception as e:
    print(f"Error: {e}")
