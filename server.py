from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

MYMEMORY_URL = "https://api.mymemory.translated.net/get"


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "TarjimaPro API ishlayapti"
    })


@app.route("/translate", methods=["GET", "POST"])
def translate():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            text = data.get("text", "")
            source = data.get("source", "auto")
            target = data.get("target", "en")
        else:
            text = request.args.get("text", "")
            source = request.args.get("source", "auto")
            target = request.args.get("target", "en")

        text = str(text).strip()
        source = str(source).strip().lower()
        target = str(target).strip().lower()

        if not text:
            return jsonify({
                "success": False,
                "error": "Tarjima qilinadigan matn kiritilmagan"
            }), 400

        if source == "auto":
            source = "en"

        langpair = f"{source}|{target}"

        response = requests.get(
            MYMEMORY_URL,
            params={
                "q": text,
                "langpair": langpair
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        translated = data.get("responseData", {}).get("translatedText", "")

        if not translated:
            return jsonify({
                "success": False,
                "error": "Tarjima natijasi olinmadi",
                "details": data
            }), 502

        return jsonify({
            "success": True,
            "source": source,
            "target": target,
            "originalText": text,
            "translatedText": translated
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Tarjima serveri javob berishi uchun vaqt tugadi"
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "error": "Tarjima xizmatiga ulanib bo‘lmadi",
            "details": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Server xatosi",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
