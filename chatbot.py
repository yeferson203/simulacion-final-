from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_session import Session
import json
import nltk
from nltk.stem import WordNetLemmatizer
import random
import os

app = Flask(__name__)
app.secret_key = "tu_secreto_muy_secreto"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

json_path = os.path.join(os.path.dirname(__file__), 'intenciones.json')

with open(json_path, encoding='utf-8') as file:
    data = json.load(file)

def find_response(message):
    message = message.lower()
    message_words = nltk.word_tokenize(message)
    message_lemmas = [lemmatizer.lemmatize(word) for word in message_words]

    best_match = {"tag": "desconocido", "score": 0}
    for intent in data["intents"]:
        for pattern in intent.get("patterns", []):
            pattern_words = nltk.word_tokenize(pattern)
            pattern_lemmas = set([lemmatizer.lemmatize(word) for word in pattern_words])
            score = sum(1 for lemma in message_lemmas if lemma in pattern_lemmas)
            if score > best_match["score"]:
                best_match = {"tag": intent["tag"], "score": score}

    if best_match["tag"] == "desconocido" or best_match["score"] == 0:
        response = random.choice(["Lo siento, no entiendo tu pregunta. ¿Puedes reformularla?"])
    else:
        for intent in data["intents"]:
            if intent["tag"] == best_match["tag"]:
                response = random.choice(intent["responses"])
                break
    
    return response

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_message = request.form['message']
        response = find_response(user_message)
        historial = session.get('historial', [])
        historial.append({"pregunta": user_message, "respuesta": response})
        session['historial'] = historial
        return jsonify({"respuesta": response})
    
    historial = session.get('historial', [])
    return render_template("index.html", historial=historial)

@app.route("/reset", methods=["POST"])
def reset():
    session['historial'] = []
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)