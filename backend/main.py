from spotify_client import get_artist_info
import json

artist_name = "Yo Yo Honey Singh"
info = get_artist_info(artist_name, album_limit=10)

print(json.dumps(info, indent=2, ensure_ascii=False))
