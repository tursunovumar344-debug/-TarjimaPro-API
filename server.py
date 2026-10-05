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


# API ishlayotganini oddiy tekshirish
@app.route("/test")
def test():
    try:
        response = requests.get(
            TRANSLATE_URL,
            params={
                "q": "I have a computer.",
                "langpair": "en|uz"
            },
            timeout=30
        )

        return jsonify({
            "server": "OK",
            "status": response.status_code,
            "result": response.json()
        })

    except Exception as e:
        return jsonify({
            "server": "ERROR",
            "error": str(e)
        }), 500


# Asosiy tarjima API
@app.route("/translate", methods=["POST"])
def translate():

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Ma'lumot yuborilmadi"
            }), 400

        text = str(data.get("text", "")).strip()
        source = str(data.get("source", "en")).strip()
        target = str(data.get("target", "uz")).strip()

        if not text:
            return jsonify({
                "error": "Tarjima qilinadigan matn bo'sh"
            }), 400

        response = requests.get(
            TRANSLATE_URL,
            params={
                "q": text,
                "langpair": f"{source}|{target}"
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        translated = (
            result
            .get("responseData", {})
            .get("translatedText", "")
        )

        if not translated:
            return jsonify({
                "error": "Tarjima natijasi olinmadi",
                "api_response": result
            }), 500

        return jsonify({
            "translatedText": translated
        }), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Tarjima serveri vaqtida javob bermadi"
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Tarjima xizmatida xatolik",
            "details": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "error": "Server xatosi",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
