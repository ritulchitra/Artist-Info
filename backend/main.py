from spotify_client import get_token

token = get_token()
print("Access token:", token)


# Calling the artist search feature
from spotify_client import search_artist

artist_name = "Honey Singh"
artist = search_artist(artist_name)

print("Artist found:")
print(artist)
print("Hello")
