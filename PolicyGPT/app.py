from flask import Flask, jsonify, render_template, request

from rag_engine import documents, query, warm_up

app = Flask(__name__)

EXAMPLES = [
    "İkametgâh belgesi nasıl alınır?",
    "SGK işe giriş bildirgesi nasıl verilir?",
    "Türk vatandaşlığına nasıl başvurulur?",
    "Vergi mükellefiyeti başvurusu nasıl yapılır?",
]


@app.route("/")
def index():
    return render_template("index.html", examples=EXAMPLES, documents=documents())


@app.post("/sor")
def ask():
    question = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Bir soru yazın."}), 400
    try:
        return jsonify(query(question))
    except Exception as error:  # Ollama not running, model missing...
        app.logger.exception("query failed")
        return jsonify({"error": f"Cevap üretilemedi: {error}"}), 500


if __name__ == "__main__":
    warm_up()
    app.run(debug=True)
