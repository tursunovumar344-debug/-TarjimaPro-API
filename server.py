import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TRANSLATE_URL = "https://api.mymemory.translated.net/get"


@app.route("/")
def home():
    return "TarjimaPro API ishlayapti!"


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()

        text = data.get("text", "").strip()
        source = data.get("source", "en")
        target = data.get("target", "uz")

        if not text:
            return jsonify({
                "error": "Matn kiritilmagan"
            }), 400

        params = {
            "q": text,
            "langpair": f"{source}|{target}"
        }

        response = requests.get(
            TRANSLATE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        translated = result.get(
            "responseData",
            {}
        ).get(
            "translatedText",
            ""
        )

        if not translated:
            return jsonify({
                "error": "Tarjima olinmadi"
            }), 500

        return jsonify({
            "translatedText": translated
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
