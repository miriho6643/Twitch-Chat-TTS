import socket
import pyttsx3
import re
import random
import time
import threading
import queue

import pystray
from PIL import Image, ImageDraw

# ================== CONFIG ==================
SERVER = "irc.chat.twitch.tv"
PORT = 6667

NICK = f"justinfan{random.randint(10000,99999)}"
CHANNEL = "#miriho6643"
# ============================================

running = True

engine = pyttsx3.init()
engine.setProperty("rate", 165)

# ------------------- IRC -------------------
msg_regex = re.compile(r":(\w+)!.* PRIVMSG #\w+ :(.*)")

def irc_loop():
    global running

    while running:
        sock = None
        try:
            sock = socket.socket()
            sock.connect((SERVER, PORT))

            sock.send(f"NICK {NICK}\r\n".encode("utf-8"))
            sock.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))

            print(f"Verbunden als {NICK}")

            while running:
                resp = sock.recv(2048).decode("utf-8", errors="ignore")
                if not resp:
                    raise ConnectionError("Verbindung verloren")

                for line in resp.split("\r\n"):
                    if line.startswith("PING"):
                        sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                        continue

                    match = msg_regex.match(line)
                    if match:
                        user, message = match.groups()
                        print(f"{user}: {message}")
                        engine.say(f"{user} sagt {message}")
                        engine.runAndWait()
                        engine.stop()

        except Exception as e:
            print("IRC Fehler:", e)
            time.sleep(5)

        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

# ------------------- TRAY -------------------
def create_image():
    image = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(image)
    d.ellipse((16, 16, 48, 48), fill="purple")
    return image

def exit_app(icon, item):
    global running
    running = False
    icon.stop()

icon = pystray.Icon(
    "TwitchTTS",
    create_image(),
    "Twitch TTS",
    menu=pystray.Menu(
        pystray.MenuItem("Beenden", exit_app)
    )
)

# ------------------- START -------------------
irc_thread = threading.Thread(target=irc_loop, daemon=True)
irc_thread.start()

icon.run()
