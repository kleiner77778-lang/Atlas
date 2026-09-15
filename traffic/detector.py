import time
import math

class TrafficDetector:
    def __init__(self):
        self.previous_speed = 0.0
        self.last_alert_time = 0.0
        self.border_crossed_ch = False

    def check_traffic(self, speed_kmh, lat, lon):
        current_time = time.time()
        speed_drop = self.previous_speed - speed_kmh
        
        if self.previous_speed > 70.0 and speed_kmh < 30.0 and speed_drop > 40.0:
            self.previous_speed = speed_kmh
            if current_time - self.last_alert_time > 180:
                self.last_alert_time = current_time
                maps_link = f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={lat}%2C{lon}"
                return {
                    "alert": True, 
                    "message": f"🚨🚨 STAU-ALARM! Abruptes Abbremsen ({round(self.previous_speed)} -> {round(speed_kmh)} km/h)!\n🔄 Umfahrung prüfen: {maps_link}"
                }

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

    def check_border_crossing(self, lat):
        # Schweizer Grenze südlich von Singen
        if lat < 47.74 and not self.border_crossed_ch:
            self.border_crossed_ch = True
            timestamp = time.strftime("%H:%M:%S")
            return f"🇨🇭 **GRENZÜBERTRITT ERKANNT**\nGrenze Richtung Schweiz um {timestamp} Uhr passiert!"
        return None

    def reset_border(self):
        self.border_crossed_ch = False
