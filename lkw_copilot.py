import time
import threading
import requests

# Globaler Speicher für das aktuelle Ziel
aktives_ziel = {"ziel": None}

def sende_an_telegram(text):
    """
    Hier wird deine bestehende Telegram-Sende-Funktion aufgerufen.
    """
    # print(f"[TELEGRAM]: {text}") # Platzhalter, durch deinen Bot ersetzen
    pass

def prüfe_verkehr_auf_route(ziel):
    """
    Prüft die Strecke im Hintergrund auf Staus.
    Gibt zurück: (stau_vorhanden, verzögerung_in_minuten, empfohlene_abfahrt)
    """
    # --- HIER DEINE ROUTEN- / OSRM-LOGIK EINBAUEN ---
    stau_vorhanden = False
    minuten = 0
    ausfahrt = ""
    
    return stau_vorhanden, minuten, ausfahrt

def background_stau_watcher():
    """
    Läuft im Hintergrund als unsichtbarer Wächter 
    und prüft alle 5 Minuten (300 Sekunden) die Strecke.
    """
    print("Hintergrund-Stauwarner gestartet...")
    while True:
        try:
            ziel = aktives_ziel.get("ziel")
            if ziel:
                stau, minuten, abfahrt = prüfe_verkehr_auf_route(ziel)
                if stau:
                    nachricht = (
                        f"🚨 **STAU-ALARM AUF DER ROUTE nach {ziel}!** 🚨\n\n"
                        f"Verzögerung: ca. {minuten} Minuten.\n"
                        f"👉 **Empfohlene Abfahrt:** Nimm **{abfahrt}**, "
                        f"um den Schlamassel zu umgehen!"
                    )
                    sende_an_telegram(nachricht)
        except Exception as e:
            print(f"Fehler im Stau-Watcher: {e}")
            
        # Alle 5 Minuten prüfen
        time.sleep(300)

def verarbeite_telegram_nachricht(nachricht_text, sender_send_func):
    """
    Fängt deine Telegram-Eingaben ab:
    - 'Start' / 'Stopp' für die Schicht
    - 'Pause' / '15' / '30' für Lenkzeit-Regeln
    - Alles andere (oder '/ziel Ort') wird sofort als neues Ziel gesetzt!
    """
    global sende_an_telegram
    sende_an_telegram = sender_send_func
    
    text = nachricht_text.strip()
    text_lower = text.lower()
    
    if text_lower == "start":
        aktives_ziel["ziel"] = None
        return "🟢 Schicht gestartet. Kilometer und Lenkzeiten werden überwacht."
        
    elif text_lower == "stopp":
        aktives_ziel["ziel"] = None  # Ziel bei Feierabend zurücksetzen
        return "🛑 Schicht beendet. Erstelle den vollständigen Feierabend-Bericht..."
        
    elif text_lower in ["pause", "15", "30"]:
        return f"☕ Pause ({text_clean} min) registriert und gespeichert."
        
    elif text_lower.startswith("/ziel"):
        ziel = text.replace("/ziel", "").strip()
        aktives_ziel["ziel"] = ziel
        return f"🎯 Ziel auf **{ziel}** gesetzt! Stauwarner läuft im Hintergrund."
        
    else:
        # Direkteingabe (z.B. einfach "Gottmadingen" in den Chat schreiben)
        aktives_ziel["ziel"] = text
        return f"🎯 Ziel auf **{text}** gesetzt! Route wird ab sofort alle 5 Minuten überwacht."

# Startet den Hintergrund-Stauwarner automatisch beim Laden des Skripts
threading.Thread(target=background_stau_watcher, daemon=True).start()
