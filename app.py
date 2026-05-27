import datetime
import random
from flask import Flask, render_template, request, jsonify
from waitress import serve

app = Flask(__name__)

FALLBACK_RESPONSES = [
    "Main samajh nahi paayi, thoda clear boliye.",
    "Is command ke baare mein mujhe abhi pata nahi hai.",
    "Kya aap dobara bol sakte ho?"
]

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "instagram": "https://www.instagram.com",
    "wikipedia": "https://www.wikipedia.com",
}

OPEN_KEYWORDS = ["open", "kholo", "chalu", "start"]
EXIT_COMMANDS = ["exit", "quit", "stop", "band ho jao"]
NAME_PROMPTS = ["mera naam", "my name is", "main hoon"]
GREETING_WORDS = ["hello", "hi", "namaste", "lassi"]
FEELING_WORDS = ["kaise ho", "how are you"]
TIME_WORDS = ["time", "samay"]
DATE_WORDS = ["date", "tarikh"]

user_state = {"user_name": None}


def command_contains(command, keywords):
    return any(k in command for k in keywords)


def get_time_response():
    now = datetime.datetime.now()
    return f"Abhi samay hai {now.hour} baj kar {now.minute} minute"


def get_date_response():
    today = datetime.date.today()
    return f"Aaj ki tareekh {today.day} {today.strftime('%B')} {today.year} hai"


def process_command(command):
    command = command.lower().strip()
    result = {"text": "", "open_url": None}

    if command_contains(command, EXIT_COMMANDS):
        result["text"] = "Goodbye! Phir milenge 👋"
        return result

    if command_contains(command, NAME_PROMPTS):
        parts = command.split()
        for kw in ["is", "hoon", "naam"]:
            if kw in parts:
                idx = parts.index(kw)
                if idx + 1 < len(parts):
                    name = parts[idx + 1].capitalize()
                    user_state["user_name"] = name
                    result["text"] = f"Nice to meet you, {name}! 😊"
                    return result
        result["text"] = "Aapka naam kya hai? Please type: my name is [your name]"
        return result

    if command_contains(command, GREETING_WORDS):
        name = user_state.get("user_name")
        result["text"] = (
            f"Namaste {name}, kaise madad kar sakti hoon? 🙏"
            if name else "Namaste! Bataiye main kya madad kar sakti hoon 🙏"
        )
        return result

    if command_contains(command, FEELING_WORDS):
        name = user_state.get("user_name")
        result["text"] = (
            f"Main bilkul theek hoon {name}! Aur aap? 😊"
            if name else "Main bilkul theek hoon! Aur aap? 😊"
        )
        return result

    if command_contains(command, TIME_WORDS):
        result["text"] = get_time_response() + " ⏰"
        return result

    if command_contains(command, DATE_WORDS):
        result["text"] = get_date_response() + " 📅"
        return result

    for name, url in WEBSITES.items():
        if name in command and command_contains(command, OPEN_KEYWORDS):
            result["text"] = f"Opening {name.capitalize()}... 🌐"
            result["open_url"] = url
            return result

    result["text"] = random.choice(FALLBACK_RESPONSES)
    return result


@app.route("/")
def index():
    response = render_template("index.html")
    from flask import make_response
    resp = make_response(response)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    command = data.get("message", "")
    response = process_command(command)
    return jsonify(response)


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
