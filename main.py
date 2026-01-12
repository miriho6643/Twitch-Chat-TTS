import socket
import pyttsx3
import re
import random
import threading
import tkinter as tk
import requests
import hashlib
import os

# ================== CONFIG ==================
SERVER = "irc.chat.twitch.tv"
PORT = 6667

NICK = f"justinfan{random.randint(10000,99999)}"
CHANNEL = "#miriho6643"   # DEIN CHANNEL
# ============================================

def update_single_file(file_url: str, local_file: str):
    """Prüft, ob die lokale Datei aktuell ist, und lädt sie bei Bedarf von GitHub herunter."""
    try:
        # Prüfen, ob GitHub erreichbar ist
        head = requests.head(file_url, timeout=5)
        if head.status_code != 200:
            print("GitHub nicht erreichbar, weiter geht's...")
            return

        # Hash der Remote-Datei
        remote_content = requests.get(file_url).content
        remote_hash = hashlib.sha256(remote_content).hexdigest()

        # Hash der lokalen Datei
        local_hash = None
        if os.path.exists(local_file):
            with open(local_file, "rb") as f:
                local_hash = hashlib.sha256(f.read()).hexdigest()

        # Vergleichen und ggf. updaten
        if local_hash != remote_hash:
            with open(local_file, "wb") as f:
                f.write(remote_content)
            print(f"{local_file} wurde aktualisiert.")
        else:
            print(f"{local_file} ist aktuell.")

    except requests.RequestException:
        print("GitHub nicht erreichbar, weiter geht's...")

# Beispielaufruf
update_single_file(
    "https://raw.githubusercontent.com/miriho6643/Twitch-Chat-TTS/main/main.py",  # URL anpassen
    "~/TwitchChatTTS/main.py"  # lokaler Pfad
)

# Text-to-Speech
tts = pyttsx3.init()
tts.setProperty("rate", 165)

def speak(text):
    tts.say(text)
    tts.runAndWait()

# ------------------- Tkinter GUI -------------------
root = tk.Tk()
root.title("Twitch Chat")
root.geometry("500x600")

chat_box = tk.Text(root, state="disabled", wrap="word")
chat_box.pack(fill="both", expand=True)

def add_message(msg):
    chat_box.config(state="normal")
    chat_box.insert("end", msg + "\n")
    chat_box.see("end")
    chat_box.config(state="disabled")
    speak(msg)  # TTS

# ------------------- IRC Socket -------------------
msg_regex = re.compile(r":(\w+)!.* PRIVMSG #\w+ :(.*)")

def irc_thread():
    try:
        sock = socket.socket()
        sock.connect((SERVER, PORT))

        # Anonymer Login
        sock.send(f"NICK {NICK}\r\n".encode("utf-8"))
        sock.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))

        add_message(f"Anonym verbunden als {NICK}")

        while True:
            resp = sock.recv(2048).decode("utf-8", errors="ignore")

            for line in resp.split("\r\n"):
                if not line:
                    continue

                # PING-PONG
                if line.startswith("PING"):
                    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                    continue

                match = msg_regex.match(line)
                if match:
                    user, message = match.groups()
                    text = f"{user} sagt: {message}"
                    root.after(0, add_message, text)  # GUI-threadsafe

    except Exception as e:
        root.after(0, add_message, f"Fehler: {e}")

# Thread starten
threading.Thread(target=irc_thread, daemon=True).start()

root.mainloop()
