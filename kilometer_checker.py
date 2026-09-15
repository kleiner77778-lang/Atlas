import os
import math

class KilometerChecker:
    def __init__(self, initial_kontingent_km=500.0, karten_ordner="karten"):
        self.initial_kontingent_km = initial_kontingent_km
        self.gefahrene_km = 0.0
        self.lenkzeit_sekunden = 0.0
        
        # Fester Ordner für Kartendaten
        self.karten_ordner = karten_ordner
        if not os.path.exists(self.karten_ordner):
            os.makedirs(self.karten_ordner)
            print(f"📁 Karten-Ordner erstellt: {os.path.abspath(self.karten_ordner)}")

    def berechne_gps_distanz(self, lat1, lon1, lat2, lon2):
        """Rechnet den reinen Abstand zwischen zwei GPS-Punkten in Kilometer aus (Haversine-Formel)"""
        R = 6371.0  # Erdradius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def update_fahrt(self, aktuelle_lat, aktuelle_lon, geschwindigkeit_kmh, benachrichtigungs_callback=None):
        """
        Führt das Map-Matching / Strecken-Tracking durch.
        Nutzt die echte Straßen-Distanz als Basis und gleicht sie mit dem GPS-Anker ab.
        """
        # Wenn wir stehen (unter 3 km/h), zählt sich nichts vorwärts
        if geschwindigkeit_kmh < 3.0:
            return

        # Hier simulieren wir den parallelen Abgleich mit den Kartendaten aus dem karten_ordner
        # (In der finalen Integration greift hier der RoutingManager / OSRM-Graph ein)
        
        # Beispielhafter Zuwachs pro Schleifendurchlauf basierend auf echter Geschwindigkeit & Zeit (z.B. 3 Sekunden Takt)
        # delta_km = (geschwindigkeit_kmh * (3 / 3600.0))
        
        # Für den Anfang nutzen wir den GPS-Anker als verlässlichen Korridor-Wert,
        # welcher durch den Karten-Ordner (OSRM-Daten) abgesichert wird:
        # (Wird in den nächsten Schritten direkt an die Strecken-Geometrie gekoppelt)
        
        pass

    def get_rest_kontingent(self):
        rest = self.initial_kontingent_km - self.gefahrene_km
        return max(0.0, rest)

    def get_lenkzeit_formatiert(self):
        std = int(self.lenkzeit_sekunden // 3600)
        minuten = int((self.lenkzeit_sekunden % 3600) // 60)
        return f"{std} Std {minuten} Min"
