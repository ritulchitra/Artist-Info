from flask import Flask, request, jsonify
from flask_cors import CORS
from .spotify_client import search_artists, get_artist_info_by_id, get_album_tracks, get_artist_top_tracks



app = Flask(__name__)
CORS(app)

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("name", "").strip()
    if not q:
        return jsonify({"results": []})
    limit = int(request.args.get("limit", 8))
    results = search_artists(q, limit=limit)
    return jsonify({"results": results})

@app.route("/artist", methods=["GET"])
def artist():
    """
    Get full artist info by id: /artist?id=ARTIST_ID
    (frontend will call by id from search results)
    """
    artist_id = request.args.get("id")
    if not artist_id:
        return jsonify({"error": "Provide ?id=ARTIST_ID"}), 400

    info = get_artist_info_by_id(artist_id, album_limit=10)
    if not info:
        return jsonify({"error": "Artist not found"}), 404
    return jsonify(info)

@app.route("/album_tracks", methods=["GET"])
def album_tracks():
    album_id = request.args.get("id")
    if not album_id:
        return jsonify({"error": "Provide ?id=ALBUM_ID"}), 400

    tracks = get_album_tracks(album_id, limit=500)
    if not tracks:
        return jsonify({"error": "No tracks found or album not found"}), 404

    return jsonify({
        "album_id": album_id,
        "tracks": tracks
    })


@app.route("/artist_top_tracks", methods=["GET"])
def artist_top_tracks():
    artist_id = request.args.get("id")
    if not artist_id:
        return jsonify({"error": "Provide ?id=ARTIST_ID"}), 400
    limit = int(request.args.get("limit", 3))
    market = request.args.get("market", "US")
    tracks = get_artist_top_tracks(artist_id, market=market, limit=limit)
    if not tracks:
        return jsonify({"error": "No top tracks found"}), 404
    return jsonify({"artist_id": artist_id, "top_tracks": tracks})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
