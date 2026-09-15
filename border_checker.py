import os
import json
import math

class BorderChecker:
    def __init__(self, grenzen_datei="bekannte_grenzen.json"):
        self.grenzen_datei = grenzen_datei
        self.grenzen = []
        self.aktive_zonen_status = {}
        self.lade_grenzen()

    def lade_grenzen(self):
        """Lädt bekannte Grenz- und Zonenpunkte aus der JSON-Datei"""
        if os.path.exists(self.grenzen_datei):
            try:
                with open(self.grenzen_datei, "r", encoding="utf-8") as f:
                    self.grenzen = json.load(f)
                print(f"📍 {len(self.grenzen)} bekannte Grenzen/Zonen geladen.")
            except Exception as e:
                print(f"Fehler beim Laden der Grenzen: {e}")
        else:
            print("⚠️ Keine bekannte_grenzen.json gefunden. Starte mit leerer Liste.")
            self.grenzen = []

    def berechne_entfernung(self, lat1, lon1, lat2, lon2):
        """Berechnet die Entfernung in Kilometern zwischen zwei GPS-Punkten"""
        try:
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.asin(math.sqrt(a))
            return 6371 * c  # Erdradius in km
        except Exception:
            return 999.0

    def pruefe_position(self, lat, lon, telegram_callback):
        """Prüft, ob eine hinterlegte Grenze oder Zone passiert wurde"""
        for grenze in self.grenzen:
            g_lat = grenze.get("lat", 0.0)
            g_lon = grenze.get("lon", 0.0)
            name = grenze.get("name", "Unbekannte Zone")
            
            distanz = self.berechne_entfernung(lat, lon, g_lat, g_lon)
            
            # Wenn man unter 500 Meter (0.5 km) an der Grenze ist
            if distanz < 0.5:
                if not self.aktive_zonen_status.get(name, False):
                    telegram_callback(f"🚨 *Grenz-/Zonen-Hinweis*\nZone erreicht: `{name}`")
                    self.aktive_zonen_status[name] = True
            else:
                self.aktive_zonen_status[name] = False

# ==========================================
# END OF FILE (EOF)
# ==========================================

