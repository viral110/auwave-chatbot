from flask import Flask, request, jsonify
from chatbot import PerplexityChatbot
import os

app = Flask(__name__)

bot = PerplexityChatbot(
    api_key=os.getenv("PPLX_API_KEY"),
    content_file_path="auwave_corpus.txt"
)

@app.route("/")
def home():
    return "✅ Auwave AI Chatbot is Live"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    reply = bot.ask_question(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
