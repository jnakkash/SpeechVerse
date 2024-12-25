from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# AudD API Key
API_KEY = "028fc09d83866df1c586a113fcc0010b"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recognize", methods=["POST"])
def recognize():
    # Receive audio file from the frontend
    file = request.files["audio"]
    if not file:
        return jsonify({"error": "No audio file provided"}), 400

    # Send the audio file to the AudD API
    response = requests.post(
        "https://api.audd.io/",
        data={"api_token": API_KEY},
        files={"file": file},
    )

    if response.status_code != 200:
        return jsonify({"error": "Failed to recognize audio"}), response.status_code

    result = response.json()

    if "result" in result:
        song = result["result"]
        artist_name = song.get("artist", "Unknown Artist")

        # Fetch other songs by the artist
        search_response = requests.get(
            "https://api.audd.io/findLyrics/",
            params={"q": artist_name, "api_token": API_KEY},
        )

        if search_response.status_code == 200:
            search_results = search_response.json().get("result", [])
        else:
            search_results = []

        return jsonify({
            "recognized_song": song,
            "other_songs": search_results,
        })
    else:
        return jsonify({"error": "No result found"})


if __name__ == "__main__":
    app.run(debug=True)
