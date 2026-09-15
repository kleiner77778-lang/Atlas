import json
import os
import time

def lade_fahrzeugdaten():
    try:
        with open("config/vehicle.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"name": "Volvo FM Electric", "gewicht_t": 18, "laenge_m": 10, "hoehe_m": 4}

def sende_telegram_nachricht(text):
    print(f"[Telegram gesendet]: {text}")

def trigger_android_warnung(distanz):
    if distanz <= 2.0 and distanz > 0:
        # 1. Android-Pop-up Benachrichtigung oben auf dem Display
        os.system('termux-notification --title "🚨 STAUWARNUNG (2 km)" --content "Empfehlung: Nächste Abfahrt nehmen!" --priority high --sound')
        # 2. Deutsche Sprachausgabe (TTS)
        os.system('termux-tts-speak "Achtung! Stau in zwei Kilometern. Bitte nächste Abfahrt nehmen."')
    elif distanz == 0.0:
        os.system('termux-tts-speak "Stau-Bereich erreicht. Umleitung aktiv."')

def verarbeite_befehl(text_eingabe):
    text_eingabe = text_eingabe.strip()
    if text_eingabe.startswith("/"):
        teile = text_eingabe.split(" ", 1)
        befehl = teile[0].lower()
        argument = teile[1] if len(teile) > 1 else ""

        if befehl == "/ende":
            sende_telegram_nachricht("🟢 Schicht beendet. Abschlussbericht wird erstellt...")
            os.system('termux-tts-speak "Schicht beendet. Gute Heimfahrt."')
            return "ende"
        elif befehl == "/status":
            sende_telegram_nachricht("📊 Status: Volvo FM Electric ist betriebsbereit. Route aktiv.")
        elif befehl == "/ziel" and argument:
            sende_telegram_nachricht(f"🎯 Ziel auf {argument} gesetzt! Route wird überwacht.")
            os.system(f'termux-tts-speak "Ziel auf {argument} gesetzt."')
    return "weiter"

def main():
    fahrzeug = lade_fahrzeugdaten()
    print(f"=== {fahrzeug.get('name', 'E-LKW')} Live-Tracker mit Stauwarner gestartet ===")
    
    sende_telegram_nachricht("🟢 Schicht gestartet. Kilometer und Zeiten werden überwacht.")
    os.system('termux-tts-speak "Schicht gestartet. System bereit."')

    # Simulierte Test-Entfernungen zur Demonstration des 2-km-Stauwarners
    simulierte_entfernungen = [5.0, 3.5, 2.0, 1.0, 0.0]

    for distanz in simulierte_entfernungen:
        print(f"\n📍 Aktuelle Distanz zum Hindernis: {distanz} km")
        
        # 2-km-Stauwarnung auslösen (prüft Offline-Daten / Distanz)
        trigger_android_warnung(distanz)
        
        # Beispielhafter Check für Telegram-Befehle während der Fahrt
        if distanz == 2.0:
            verarbeite_befehl("/status")
        
        time.sleep(2)

    # Am Ende Schicht sauber abschließen
    verarbeite_befehl("/ende")

if __name__ == "__main__":
    main()
