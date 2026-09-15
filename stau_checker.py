import time
import math

class StauChecker:
    def __init__(self):
        self.letzte_pruefung = 0.0
        self.stau_aktiv = False
        self.letzte_geschwindigkeit = 50.0  # km/h
        self.aktuelle_lat = 0.0
        self.aktuelle_lon = 0.0

    def set_aktuelle_position(self, lat, lon):
        self.aktuelle_lat = lat
        self.aktuelle_lon = lon

    def set_aktuelle_geschwindigkeit(self, geschwindigkeit_kmh):
        self.letzte_geschwindigkeit = geschwindigkeit_kmh

    def berechne_distanz_m(self, lat1, lon1, lat2, lon2):
        """Berechnet Entfernung in Metern zwischen zwei Punkten"""
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def pruefe_stau(self, stau_punkte, telegram_callback):
        """
        Prüft exakt einmal pro Minute:
        1. Ob sich das Fahrzeug einem bekannten Staupunkt auf 2 km nähert.
        2. Ob die Geschwindigkeit unerwartet unter 5 km/h fällt (plötzlicher Stillstand).
        """
        jetzt = time.time()
        
        # Exakter 60-Sekunden-Takt (1 Mal pro Minute)
        if jetzt - self.letzte_pruefung < 60:
            return
            
        self.letzte_pruefung = jetzt

        # 1. Prüfung auf anstehende Staupunkte (2 km / 2000 Meter Vorwarnung)
        for stau in stau_punkte:
            s_lat = stau.get("lat")
            s_lon = stau.get("lon")
            s_grund = stau.get("grund", "Verkehrsstockung")
            s_abfahrt = stau.get("umfahrung", "Nächste Ausfahrt nutzen")
            
            if s_lat and s_lon and self.aktuelle_lat and self.aktuelle_lon:
                distanz = self.berechne_distanz_m(self.aktuelle_lat, self.aktuelle_lon, s_lat, s_lon)
                
                # Warnung bei ca. 2 Kilometern Abstand
                if distanz <= 2000 and not stau.get("gemeldet", False):
                    warn_text = (
                        f"🚨 *Stau-Vorwarnung (ca. {int(distanz)}m)*\n"
                        f"Grund: {s_grund}\n"
                        f"👉 *Empfehlung:* {s_abfahrt}"
                    )
                    telegram_callback(warn_text)
                    stau["gemeldet"] = True  # Verhindert Mehrfach-Spam für diesen Punkt

        # 2. Allgemeine Stillstands-Überwachung im 1-Minuten-Takt
        if self.letzte_geschwindigkeit < 5.0:
            if not self.stau_aktiv:
                telegram_callback("⚠️ *Stillstand erkannt!*\nGeschwindigkeit unter 5 km/h. Prüfe Ausweichroute / Abfahrt.")
                self.stau_aktiv = True
        else:
            self.stau_aktiv = False

# ==========================================
# END OF FILE (EOF)
# ==========================================
