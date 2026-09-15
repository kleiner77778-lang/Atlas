import os

def speak(text):
    """Gibt Warnungen und Hinweise per Sprachausgabe (Android Termux-TTS) aus."""
    print(f"[AUDIO SPRACHAUSGABE] {text}")
    try:
        os.system(f"termux-tts-speak '{text}'")
    except Exception as e:
        print(f"[AUDIO FEHLER] Konnte Sprachausgabe nicht ausführen: {e}")
