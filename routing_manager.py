import os
import json
import requests

class RoutingManager:
    def __init__(self, offline_datei="bekannte_ziele.json"):
        self.offline_datei = offline_datei
        self.ziel_name = ""
        self.ziel_lat = None
        self.ziel_lon = None

    def lade_offline_ziel(self, ortschaft):
        """Prüft, ob der Ort in einer lokalen JSON-Datei auf dem Handy liegt (für Offline-Modus)"""
        if os.path.exists(self.offline_datei):
            try:
                with open(self.offline_datei, "r", encoding="utf-8") as f:
                    ziele = json.load(f)
                    for z in ziele:
                        if z.get("name", "").lower() == ortschaft.lower():
                            return z.get("lat"), z.get("lon")
            except Exception as e:
                print(f"Fehler beim Laden der Offline-Ziele: {e}")
        return None, None

    def setze_ziel(self, ortschaft):
        """Setzt das Ziel: Versucht erst lokal (Offline-Karte/JSON), dann Online (Nominatim API)"""
        # 1. Erst lokal in Termux / JSON nachschauen
        lat, lon = self.lade_offline_ziel(ortschaft)
        if lat is not None and lon is not None:
            self.ziel_name = ortschaft
            self.ziel_lat = lat
            self.ziel_lon = lon
            return True, f"🎯 Offline-Ziel geladen: *{ortschaft}* ({lat:.4f}, {lon:.4f})"

        # 2. Wenn nicht lokal vorhanden, über Internet (Nominatim) auflösen
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": ortschaft,
                "format": "json",
                "limit": 1
            }
            headers = {"User-Agent": "ATLAS-TruckTracker/1.0"}
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                daten = response.json()
                if daten:
                    self.ziel_name = ortschaft
                    self.ziel_lat = float(daten[0]["lat"])
                    self.ziel_lon = float(daten[0]["lon"])
                    return True, f"🎯 Online-Ziel gesetzt: *{ortschaft}* ({self.ziel_lat:.4f}, {self.ziel_lon:.4f})"
        except Exception as e:
            print(f"Routing Online-Fehler: {e}")
            
        return False, f"❌ Konnte Ziel '{ortschaft}' weder lokal noch online finden."

# ==========================================
# END OF FILE (EOF)
# ==========================================
