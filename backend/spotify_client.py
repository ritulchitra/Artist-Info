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
    

# Get Followers
def get_artist_followers(artist_id):
    token = get_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    return data["followers"]["total"]

#Get Albums
def get_artist_albums(artist_id, limit=10):
    token = get_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {"limit": limit, "include_groups": "album,single"}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return data["items"]


#Get Songs from Album
def get_album_tracks(album_id):
    token = get_token()
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    return data["items"]


# Artist Info
def get_artist_info(artist_name, album_limit=10):
    """
    Returns a dict with artist metadata, followers, albums (with id, name, release_date)
    and tracks for each album (track id + name + duration_ms).
    """
    artist = search_artist(artist_name)
    if not artist:
        return None

    artist_id = artist["id"]
    info = {
        "id": artist_id,
        "name": artist.get("name"),
        "followers": artist.get("followers", {}).get("total"),
        "genres": artist.get("genres", []),
        "images": artist.get("images", []),
        "popularity": artist.get("popularity"),
        "albums": []
    }

    albums = get_artist_albums(artist_id, limit=album_limit) or []
    # optional: avoid exact duplicate album names
    seen = set()
    for a in albums:
        album_name = a.get("name")
        if album_name in seen:
            continue
        seen.add(album_name)

        album_entry = {
            "id": a.get("id"),
            "name": album_name,
            "release_date": a.get("release_date"),
            "total_tracks": a.get("total_tracks"),
            "tracks": []
        }

        tracks = get_album_tracks(a.get("id")) or []
        for t in tracks:
            album_entry["tracks"].append({
                "id": t.get("id"),
                "name": t.get("name"),
                "duration_ms": t.get("duration_ms")
            })

        info["albums"].append(album_entry)

    return info

