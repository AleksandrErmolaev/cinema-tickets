import requests

BASE = "https://api.tvmaze.com"

def get_popular_shows():
    url = f"{BASE}/shows"
    return requests.get(url).json()