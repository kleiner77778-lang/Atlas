import math
import time

class NavBackend:
    def __init__(self):
        self.odometer_km = 0.0      
        self.energy_kwh = 0.0       
        self.last_lat = None
        self.last_lon = None
        
        self.stopped_since = None
        self.pause_reported = False
        self.previous_speed = 0.0
        self.last_alert_time = 0.0  # Sperre, damit Alarme nicht spammen

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def update_metrics(self, current_lat, current_lon, speed_kmh):
        if self.last_lat is not None and self.last_lon is not None:
            dist = self.calculate_distance(self.last_lat, self.last_lon, current_lat, current_lon)
            if dist < 5.0:
                self.odometer_km += dist
                self.energy_kwh += dist * 1.2 

        self.last_lat = current_lat
        self.last_lon = current_lon

        return {
            "odometer_km": round(self.odometer_km, 2),
            "energy_kwh": round(self.energy_kwh, 2),
            "speed_kmh": round(speed_kmh, 1)
        }

    def check_traffic(self, speed_kmh, lat, lon):
        current_time = time.time()
        speed_drop = self.previous_speed - speed_kmh
        
        # Stau-Früherkennung bei starkem Geschwindigkeitsabfall von >70 auf <30
        # Sperre von 3 Minuten, damit es nicht dauernd klingelt
        if self.previous_speed > 70.0 and speed_kmh < 30.0 and speed_drop > 40.0:
            self.previous_speed = speed_kmh
            if current_time - self.last_alert_time > 180:
                self.last_alert_time = current_time
                maps_link = f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={lat}%2C{lon}"
                return {
                    "alert": True, 
                    "message": f"🚨🚨 STAU-ALARM! Abruptes Abbremsen ({round(self.previous_speed)} -> {round(speed_kmh)} km/h)!\n🔄 Umfahrung prüfen: {maps_link}"
                }

        # Stillstand
        if speed_kmh < 5.0 and self.previous_speed > 30.0:
            if current_time - self.last_alert_time > 180:
                self.last_alert_time = current_time
                maps_link = f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={lat}%2C{lon}"
                return {
                    "alert": True, 
                    "message": f"🚨 STILLSTAND ERKANNT! Sofortige Umfahrung prüfen:\n🔄 {maps_link}"
                }
            
        self.previous_speed = speed_kmh
        return {"alert": False, "message": ""}

    def check_pause(self, speed_kmh):
        current_time = time.time()
        if speed_kmh < 2.0:
            if self.stopped_since is None:
                self.stopped_since = current_time
                self.pause_reported = False
            else:
                elapsed_pause_minutes = (current_time - self.stopped_since) / 60
                if elapsed_pause_minutes >= 15 and not self.pause_reported:
                    self.pause_reported = True
                    return "⏸️ Längere Pause erkannt: Das Fahrzeug steht seit über 15 Minuten."
        else:
            self.stopped_since = None
            self.pause_reported = False
            
        return None
