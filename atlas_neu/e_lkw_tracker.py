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
    # Hier wird die Nachricht an deinen Telegram-Bot gesendet
    print(f"[Telegram gesendet]: {text}")

def verarbeite_befehl(text_eingabe):
    text_eingabe = text_eingabe.strip()
    if text_eingabe.startswith("/"):
        teile = text_eingabe.split(" ", 1)
        befehl = teile[0].lower()
        argument = teile[1] if len(teile) > 1 else ""

        if befehl == "/ende":
            sende_telegram_nachricht("🟢 Schicht beendet. Abschlussbericht wird erstellt...")
            return "ende"
        elif befehl == "/status":
            sende_telegram_nachricht("📊 Status: Volvo FM Electric ist betriebsbereit. Route aktiv.")
        elif befehl == "/ziel" and argument:
            sende_telegram_nachricht(f"🎯 Ziel auf {argument} gesetzt! Route wird überwacht.")
    return "weiter"

def main():
    fahrzeug = lade_fahrzeugdaten()
    print(f"=== {fahrzeug.get('name', 'E-LKW')} Live-Tracker (Neu) gestartet ===")
    
    # Start-Nachricht senden
    sende_telegram_nachricht("🟢 Schicht gestartet. Kilometer und Zeiten werden überwacht.")

    # Beispielhafter Testlauf der Befehlsverarbeitung
    test_eingaben = ["/ziel beringen", "/status", "/ende"]
    for befehl in test_eingaben:
        print(f"\nEmpfangen: {befehl}")
        status = verarbeite_befehl(befehl)
        if status == "ende":
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
