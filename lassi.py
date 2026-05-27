import datetime
import os
import random
import tempfile
import webbrowser
from pathlib import Path

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

VOICE_FILE = Path("voice.mp3")
FALLBACK_RESPONSES = [
    "Main samajh nahi paayi, thoda clear boliye.",
    "Is command ke baare mein mujhe abhi pata nahi hai.",
    "Kya aap dobara bol sakte ho?"
]
OPEN_KEYWORDS = ["open", "kholo", "chalu", "start"]
CLOSE_KEYWORDS = ["close", "band", "quit"]

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "instagram": "https://www.instagram.com",
    "wikipedia": "https://www.wikipedia.com",
}

APPLICATIONS = {
    "calculator": lambda: os.system("calc"),
    "notepad": lambda: os.system("notepad"),
    "paint": lambda: os.system("mspaint"),
    "command prompt": lambda: os.system("cmd"),
    "file explorer": lambda: os.system("explorer"),
    "settings": lambda: os.startfile("ms-settings:"),
    "task manager": lambda: os.system("taskmgr"),
    "chrome": lambda: os.startfile("chrome"),
    "edge": lambda: os.startfile("msedge:"),
}

CLOSE_APPS = {
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "notepad": "notepad.exe",
    "calculator": "Calculator.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
}

EXIT_COMMANDS = ["exit", "quit", "stop", "band ho jao"]
NAME_PROMPTS = ["mera naam", "my name is", "main hoon"]
GREETING_WORDS = ["hello", "hi", "namaste", "lassi"]
FEELING_WORDS = ["kaise ho", "how are you"]
TIME_WORDS = ["time", "samay"]
DATE_WORDS = ["date", "tarikh"]


def speak_indian(text: str) -> None:
    """Speak text using Indian Hindi voice."""
    try:
        tts = gTTS(text=text, lang="hi", tld="co.in")
        tts.save(VOICE_FILE.as_posix())
        playsound(VOICE_FILE.as_posix())
    except Exception as exc:
        print("Voice error:", exc)
    finally:
        if VOICE_FILE.exists():
            try:
                VOICE_FILE.unlink()
            except OSError:
                pass


def listen_command() -> str:
    """Listen for speech and return the recognized command."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio, language="en-IN")
        print("You said:", query)
        return query.lower().strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        print("Speech service error:", exc)
        speak_indian("Speech service error")
        return ""


def command_contains(command: str, keywords: list[str]) -> bool:
    return any(keyword in command for keyword in keywords)


def open_website(command: str) -> bool:
    for name, url in WEBSITES.items():
        if name in command and command_contains(command, OPEN_KEYWORDS):
            speak_indian(f"Opening {name}")
            webbrowser.open(url)
            return True
    return False


def open_application(command: str) -> bool:
    for name, action in APPLICATIONS.items():
        if name in command and command_contains(command, OPEN_KEYWORDS):
            speak_indian(f"Opening {name}")
            action()
            return True
    return False


def close_application(command: str) -> bool:
    for name, process in CLOSE_APPS.items():
        if name in command and command_contains(command, CLOSE_KEYWORDS):
            speak_indian(f"Closing {name}")
            os.system(f"taskkill /F /IM {process}")
            return True
    return False


def get_time_response() -> str:
    now = datetime.datetime.now()
    return f"Abhi samay hai {now.hour} baj kar {now.minute} minute"


def get_date_response() -> str:
    today = datetime.date.today()
    return f"Aaj ki tareekh {today.day} {today.strftime('%B')} {today.year} hai"


def ask_name() -> str:
    speak_indian("Aapka naam kya hai?")
    return listen_command()


def main() -> None:
    state = {"user_name": None}
    print("Lassi.AI")
    speak_indian("Hello, I am Lassi AI")

    while True:
        command = listen_command()
        if not command:
            speak_indian(random.choice(FALLBACK_RESPONSES))
            continue

        handled = False

        if command_contains(command, NAME_PROMPTS):
            name = ask_name()
            if name:
                state["user_name"] = name
                speak_indian(f"Nice to meet you {name}")
            handled = True

        elif command_contains(command, GREETING_WORDS):
            if state["user_name"]:
                speak_indian(f"Namaste {state['user_name']}, kaise madad kar sakti hoon?")
            else:
                speak_indian("Namaste! Bataiye main kya madad kar sakti hoon")
            handled = True

        elif command_contains(command, FEELING_WORDS):
            if state["user_name"]:
                speak_indian(f"Main bilkul theek hoon {state['user_name']}")
            else:
                speak_indian("Main bilkul theek hoon")
            handled = True

        elif command_contains(command, TIME_WORDS):
            speak_indian(get_time_response())
            handled = True

        elif command_contains(command, DATE_WORDS):
            speak_indian(get_date_response())
            handled = True

        elif open_website(command) or open_application(command) or close_application(command):
            handled = True

        elif command_contains(command, EXIT_COMMANDS):
            speak_indian("Goodbye! Phir milenge")
            break

        if not handled:
            speak_indian(random.choice(FALLBACK_RESPONSES))


if __name__ == "__main__":
    main()

