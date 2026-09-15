import time
import math

class ShiftReport:
    def __init__(self):
        self.shift_start_time = None
        self.total_driving_seconds = 0.0
        self.last_tick_time = None
        self.odometer_km = 0.0
        self.energy_kwh = 0.0
        self.last_lat = None
        self.last_lon = None
        self.stopped_since = None
        self.pause_reported = False

    def start_shift(self):
        self.shift_start_time = time.time()
        self.last_tick_time = time.time()
        self.odometer_km = 0.0
        self.energy_kwh = 0.0
        self.total_driving_seconds = 0.0

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
        current_time = time.time()
        if self.last_tick_time is not None:
            delta_t = current_time - self.last_tick_time
            if speed_kmh > 2.0:
                self.total_driving_seconds += delta_t
        self.last_tick_time = current_time

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

    def get_current_metrics(self):
        return {
            "odometer_km": round(self.odometer_km, 2),
            "energy_kwh": round(self.energy_kwh, 2)
        }

    def get_shift_report(self):
        if not self.shift_start_time:
            return "⚠️ Keine aktive Schicht aufgezeichnet."
        
        total_shift_seconds = time.time() - self.shift_start_time
        work_hours = round(total_shift_seconds / 3600, 2)
        driving_hours = round(self.total_driving_seconds / 3600, 2)
        
        return (
            f"📋 **SCHICHTBERICHT** 📋\n"
            f"──────────────────\n"
            f"⏱️ Arbeitszeit: {work_hours} Std.\n"
            f"🚛 Fahrzeit: {driving_hours} Std.\n"
            f"🛣️ Strecke: {round(self.odometer_km, 2)} km\n"
            f"⚡ Energie: {round(self.energy_kwh, 2)} kWh\n"
            f"──────────────────"
        )
