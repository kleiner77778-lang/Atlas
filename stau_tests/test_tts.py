import time
import os

def teste_tts():
    print("=== TTS & Android-Benachrichtigung Test ===")
    
    # 1. Benachrichtigung auf dem Bildschirm oben anzeigen
    os.system('termux-notification --title "🚨 ATLAS TEST" --content "TTS und Benachrichtigung aktiv!" --priority high --sound')
    
    # 2. Sprachausgabe auf Deutsch testen
    os.system('termux-tts-speak "Systemtest erfolgreich. Sprachausgabe und Stauwarnung betriebsbereit."')
    
    print("Test-Nachricht gesendet und gesprochen.")

if __name__ == "__main__":
    teste_tts()
