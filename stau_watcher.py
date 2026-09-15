import time
import threading
import requests

def starte_automatischen_stau_warner(telegram_send_func, get_aktuelle_position_func, aktives_ziel):
    """
    Läuft im Hintergrund, prüft alle 5 Minuten die Route 
    und meldet Staus sofort via Telegram.
    """
    def background_loop():
        print("Hintergrund-Stauwarner gestartet...")
        while True:
            try:
                # Prüfen, ob überhaupt ein Ziel gesetzt wurde
                if aktives_ziel.get("ziel"):
                    current_pos = get_aktuelle_position_func()
                    destination = aktives_ziel["ziel"]
                    
                    # Hier greift deine OSRM- oder Routen-Abfrage mit Verkehrsinfos
                    # (Beispiel-Logik für den Stau-Check)
                    stau_erkannt, verzögerung_min, empfohlene_abfahrt = prüfe_verkehr_auf_route(current_pos, destination)
                    
                    if stau_erkannt:
                        nachricht = (
                            f"🚨 **STAU-ALARM AUF DER ROUTE!** 🚨\n\n"
                            f"Verzögerung: ca. {verzögerung_min} Minuten.\n"
                            f"👉 **Empfohlene Abfahrt:** Nimm unbedingt **{empfohlene_abfahrt}**, "
                            f"um den Schlamassel zu umgehen!"
                        )
                        # Sofort an Telegram senden
                        telegram_send_func(nachricht)
                
            except Exception as e:
                print(f"Fehler im Stau-Watcher: {e}")
                
            # Alle 5 Minuten (300 Sekunden) prüfen
            time.sleep(300)

    # Startet den Watcher als unsichtbaren Hintergrund-Dienst
    t = threading.Thread(target=background_loop, daemon=True)
    t.start()

def prüfe_verkehr_auf_route(start_pos, ziel):
    """
    Platzhalter für deine OSRM / Verkehrs-API Abfrage.
    Gibt zurück: (stau_vorhanden (True/False), minuten, ausfahrt_name)
    """
    # --- HIER DEINE ECHTE API-ABFRAGE EINBAUEN ---
    # Beispiel-Dummy:
    stau_vorhanden = False 
    minuten = 0
    ausfahrt = ""
    
    return stau_vorhanden, minuten, ausfahrt

# ==========================================
# WIE DU ES IN DEINEN TRACKER EINBAUST:
# ==========================================
# 
# 1. Definiere ein gemeinsames Ziel-Objekt (z.B. global oder in deiner App-Klasse):
#    aktives_ziel = {"ziel": None}
#
# 2. Wenn du morgens dein Ziel eingibst (oder per Telegram /ziel Frankfurt):
#    aktives_ziel["ziel"] = "Frankfurt"
#
# 3. Starte den Watcher einmalig beim Programmstart:
#    starte_automatischen_stau_warner(sende_an_telegram,hole_gps_daten, aktives_ziel)
