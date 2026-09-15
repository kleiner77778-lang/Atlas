import subprocess

def trigger_loud_alarm(text="Achtung! Verkehrshinweis prüfen."):
    try:
        subprocess.run(["termux-volume", "stream", "15"], capture_output=True)
        subprocess.run(["termux-tts-speak", text], capture_output=True)
    except Exception:
        pass
