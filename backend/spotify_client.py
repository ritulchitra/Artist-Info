import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_token():
    url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    data = auth_response.json()
    return data["access_token"]


# Artist seatch feature
def search_artist(name):
    token = get_token()
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": name,
        "type": "artist",
        "limit": 1
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data["artists"]["items"]:
        return data["artists"]["items"][0]   # first result
    else:
        return None
print("Hello")
