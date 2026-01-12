import os
import subprocess
import sys

def update_or_clone_repo():
    """Installiert oder updated das TwitchChatTTS-Repo in ~/TwitchChatTTS/"""
    
    # 1️⃣ requests sicherstellen
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        import requests

    GITHUB_API = "https://api.github.com/repos/miriho6643/Twitch-Chat-TTS"
    GITHUB_REPO = "https://github.com/miriho6643/Twitch-Chat-TTS.git"
    TARGET_DIR = os.path.expanduser("~/TwitchChatTTS")

    # 2️⃣ Prüfen, ob GitHub erreichbar ist
    try:
        response = requests.get(GITHUB_API, timeout=5)
        if response.status_code != 200:
            print("GitHub nicht erreichbar, weiter geht's...")
            return
    except requests.RequestException:
        print("GitHub nicht erreichbar, weiter geht's...")
        return

    # 3️⃣ Repo klonen oder updaten
    if not os.path.exists(TARGET_DIR):
        print(f"Cloning repo into {TARGET_DIR}...")
        subprocess.run(["git", "clone", GITHUB_REPO, TARGET_DIR], check=True)
        print("Clone finished.")
    else:
        print(f"Repo exists in {TARGET_DIR}, checking for updates...")
        try:
            # Fetch remote changes
            subprocess.run(["git", "fetch"], cwd=TARGET_DIR, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Vergleiche lokale HEAD mit Remote
            local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=TARGET_DIR).strip()
            remote = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=TARGET_DIR).strip()
            if local != remote:
                print("Updating repository...")
                subprocess.run(["git", "pull"], cwd=TARGET_DIR, check=False)
                print("Update finished.")
            else:
                print("Repository is already up to date.")
        except subprocess.SubprocessError:
            print("Fehler beim Prüfen oder Updaten des Repos, überspringe...")

# Funktion aufrufen
update_or_clone_repo()
