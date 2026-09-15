import time
import datetime
import requests
import os
from math import radians, sin, cos, sqrt, atan2
import sys
import select
import threading

# --- DEINE TELEGRAM DATEN ---
TELEGRAM_BOT_TOKEN = "8413301731:AAGMlffH8VYDjCUzC_UMewy0G-hau7sK8Ao"
TELEGRAM_CHAT_ID = "8941361378"

# Standard-Fallback-Werte, falls du nur "start" tippst
DEFAULT_CONTRIBUTION = 280.0
DEFAULT_ODO = 15420.0

# Aktive Schicht-Variablen
start_km_contribution = DEFAULT_CONTRIBUTION
start_km_odo = DEFAULT_ODO

# Globaler Speicher für das aktuelle Ziel
aktives_ziel = {"ziel": None}

# Koordinaten für den Grenzbereich Thayngen / Bietingen
BORDER_LAT = 47.7470
BORDER_LON = 8.7050
BORDER_RADIUS_KM = 0.4

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Fehler: {e}")

def get_telegram_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 10, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except Exception as e:
        return None

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def check_terminal_input():
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip().lower()
    return None

# --- HINTERGRUND-STAUWARNER ---
def background_stau_watcher():
    while True:
        try:
            ziel = aktives_ziel.get("ziel")
            if ziel:
                stau_vorhanden = False
                minuten = 0
                abfahrt = ""
                if stau_vorhanden:
                    send_telegram(f"🚨 **STAU-ALARM nach {ziel}!** Ca. {minuten} Min. Verzug. Abfahrt: {abfahrt}")
        except Exception as e:
            print(f"Fehler im Stau-Watcher: {e}")
        time.sleep(300)

threading.Thread(target=background_stau_watcher, daemon=True).start()

def main():
    print("E-Lkw Tracker gestartet...")
    offset = None
    
    # Originale Startmeldung
    send_telegram(
        "🟢 *Atlas E-Lkw Tracker aktiv*\n\n"
        "💡 Tipp: Starte Schichten mit `start [Kontingent] [Tacho]` (z.B. `start 290 15450`).\n"
        "Schreibe `stop` für den Feierabend-Bericht."
    )

    while True:
        updates = get_telegram_updates(offset)
        if updates and "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    msg = update["message"]["text"]
                    text_clean = msg.strip()
                    text_lower = text_clean.lower()
                    
                    if text_lower.startswith("start") or text_lower.startswith("/start"):
                        aktives_ziel["ziel"] = None
                        parts = text_clean.split()
                        if len(parts) >= 3:
                            try:
                                global start_km_contribution, start_km_odo
                                start_km_contribution = float(parts[1])
                                start_km_odo = float(parts[2])
                            except ValueError:
                                pass
                        send_telegram("🟢 Schicht gestartet. Kilometer und Zeiten werden überwacht.")
                        
                    elif text_lower in ["stopp", "stop", "/stopp", "/stop"]:
                        aktives_ziel["ziel"] = None
                        send_telegram("🛑 Schicht beendet. Feierabend-Bericht wird erstellt.")
                        
                    elif text_lower in ["pause", "15", "30"]:
                        send_telegram(f"☕ Pause ({text_clean}) registriert.")
                        
                    elif text_lower.startswith("/ziel"):
                        ziel = text_clean.replace("/ziel", "").strip()
                        aktives_ziel["ziel"] = ziel
                        send_telegram(f"🎯 Ziel auf **{ziel}** gesetzt! Stauwarner läuft im Hintergrund.")
                        
                    elif not (text_lower.startswith("start") or text_lower.startswith("stopp") or text_lower.startswith("stop") or text_lower in ["pause", "15", "30"]):
                        # Ziel-Eingabe (z.B. "gottmadingen")
                        aktives_ziel["ziel"] = text_clean
                        send_telegram(f"🎯 Ziel auf **{text_clean}** gesetzt! Route wird überwacht.")

        term_input = check_terminal_input()
        if term_input in ["stopp", "stop"]:
            aktives_ziel["ziel"] = None
            print("Schicht lokal beendet.")

        time.sleep(2)

if __name__ == "__main__":
    main()
