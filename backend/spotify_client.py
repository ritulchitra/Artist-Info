import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# inside spotify_client.py (replace old get_token)
import time
from requests import Session

_session = Session()        # reuse TCP connection
_token_cache = {"token": None, "expires_at": 0}

def get_token():
    now = int(time.time())
    if _token_cache["token"] and now < _token_cache["expires_at"] - 10:
        return _token_cache["token"]

    url = "https://accounts.spotify.com/api/token"
    resp = _session.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    expires_in = data.get("expires_in", 3600)
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + int(expires_in)
    return token



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
def get_artist_info(artist_name, album_limit=5):
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

def get_artist_top_tracks(artist_id, market="US", limit=3):
    """
    Return the artist's top tracks (Spotify endpoint) — ordered by Spotify popularity.
    """
    token = get_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"market": market}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        return []
    items = r.json().get("tracks", [])
    # map to simple shape and limit
    mapped = [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "duration_ms": t.get("duration_ms"),
            "popularity": t.get("popularity"),
            "preview_url": t.get("preview_url"),
            "track_number": t.get("track_number"),
            "album": {
                "id": (t.get("album") or {}).get("id"),
                "name": (t.get("album") or {}).get("name"),
                "image": (t.get("album") or {}).get("images", [{}])[0].get("url")
            }
        }
        for t in items
    ]
    return mapped[:limit]


def search_artists(name, limit=5):
    """Return small list of matching artists (id, name, followers, image, genres)."""
    token = get_token()
    url = "https://api.spotify.com/v1/search"
    params = {"q": name, "type": "artist", "limit": limit}
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, params=params)
    items = r.json().get("artists", {}).get("items", [])
    return [
        {
            "id": it["id"],
            "name": it["name"],
            "followers": it.get("followers", {}).get("total"),
            "image": (it.get("images") or [{}])[0].get("url"),
            "genres": it.get("genres", []),
            "popularity": it.get("popularity")
        }
        for it in items
    ]

def get_artist_by_id(artist_id):
    """Return the raw artist object for a given artist_id."""
    token = get_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    return r.json()
# robust get_album_tracks replacement
import time
from requests import Session

_session = Session()  # ensure you have a Session at module top (shared with get_token)

def get_album_tracks(album_id, limit=500):
    """
    Return all tracks for an album (handles paging). Returns list of tracks with id,name,duration_ms,track_number.
    """
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    base_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    params = {"limit": 50, "offset": 0}
    all_items = []

    try:
        while True:
            resp = _session.get(base_url, headers=headers, params=params, timeout=10)
            if resp.status_code != 200:
                # return empty list on error (caller will show message)
                return []
            data = resp.json()
            items = data.get("items", [])
            for t in items:
                all_items.append({
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "duration_ms": t.get("duration_ms"),
                    "track_number": t.get("track_number")
                })
            # paging
            if data.get("next"):
                params["offset"] += params["limit"]
                # small sleep to avoid hitting rate limits on loops
                time.sleep(0.05)
                # continue loop
            else:
                break
            # stop early if we've gathered requested limit
            if limit and len(all_items) >= limit:
                break
    except Exception as e:
        # on exception, return what we have (or empty)
        return all_items or []

    # ensure we respect requested limit
    return all_items[:limit]


# spotify_client.py (replace get_artist_info_by_id)
def get_artist_info_by_id(artist_id, album_limit=10):
    """Return artist metadata + albums WITHOUT tracks (faster)."""
    artist = get_artist_by_id(artist_id)
    if not artist:
        return None

    info = {
        "id": artist.get("id"),
        "name": artist.get("name"),
        "followers": artist.get("followers", {}).get("total"),
        "genres": artist.get("genres", []),
        "images": artist.get("images", []),
        "popularity": artist.get("popularity"),
        "albums": []
    }

    albums = get_artist_albums(artist.get("id"), limit=album_limit) or []
    seen = set()
    for a in albums:
        name = a.get("name")
        if name in seen:
            continue
        seen.add(name)

        info["albums"].append({
            "id": a.get("id"),
            "name": name,
            "release_date": a.get("release_date"),
            "total_tracks": a.get("total_tracks"),
            "image": (a.get("images") or [{}])[0].get("url")
            # NOTE: no "tracks" field here
        })

    return info

