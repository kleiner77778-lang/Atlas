import time
from core.dashboard_ui import dashboard_data
from audio.speech_engine import speak

class TruckTachoAndTrafficManager:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.current_driving_mins = 0.0
        self.total_km_driven = 0.0
        self.initial_tacho = 0.0
        self.initial_contingent = 0.0
        self.is_moving = False
        self.stationary_start_time = None
        self.auto_work_triggered = False
        self.pause_prompt_active = False
        
        # Realistische Batterie-Werte für Volvo FM Electric
        self.battery_kwh_max = 540.0
        self.battery_kwh_current = 486.0
        self.battery_soc = 90.0

    def set_start_values(self, contingent, tacho_start):
        self.initial_contingent = float(contingent)
        self.initial_tacho = float(tacho_start)
        self.total_km_driven = float(tacho_start)
        dashboard_data["tacho"] = self.total_km_driven

    def update_telematics(self, speed_kmh, distance_delta_km):
        now = time.time()
        
        if speed_kmh > 5.0:
            self.is_moving = True
            self.stationary_start_time = None
            self.auto_work_triggered = False
            self.pause_prompt_active = False
            
            delta_mins = 2.0 / 60.0
            self.current_driving_mins += delta_mins
            self.total_km_driven += distance_delta_km
            
            # Energieverbrauch pro km
            energy_used = distance_delta_km * 1.2
            self.battery_kwh_current = max(0.0, self.battery_kwh_current - energy_used)
        else:
            if self.is_moving:
                self.is_moving = False
                self.stationary_start_time = now
                
            self.battery_kwh_current = max(0.0, self.battery_kwh_current - 0.02)
            
            if self.stationary_start_time:
                standing_mins = (now - self.stationary_start_time) / 60.0
                if standing_mins >= 6.0 and not self.auto_work_triggered:
                    self.auto_work_triggered = True
                    msg = "Automatische Arbeitszeit erkannt wegen Stillstand."
                    self.bot.send_message(f"⏱️ {msg}")
                    speak(msg)
                
                if standing_mins >= 5.0 and not self.pause_prompt_active:
                    self.pause_prompt_active = True
                    msg = "Du stehst seit 5 Minuten. Machst du jetzt Pause? Antworte mit Ja oder Nein."
                    self.bot.send_message(f"☕ {msg}")
                    speak("Du stehst seit fünf Minuten. Machst du jetzt Pause?")

        # Berechnungen für Dashboard
        self.battery_soc = round((self.battery_kwh_current / self.battery_kwh_max) * 100.0, 1)
        dashboard_data["driving_mins"] = int(self.current_driving_mins)
        dashboard_data["tacho"] = round(self.total_km_driven, 1)
        dashboard_data["battery_soc"] = self.battery_soc
        dashboard_data["battery_kwh"] = round(self.battery_kwh_current, 1)
        
        # Rest-Kontingent dynamisch anpassen (Start-Kontingent minus gefahrene km)
        if self.initial_contingent > 0:
            km_driven = self.total_km_driven - self.initial_tacho
            rest_contingent = max(0.0, self.initial_contingent - km_driven)
            dashboard_data["contingent"] = f"{rest_contingent:.1f} km"

        if self.battery_soc <= 20.0 and self.battery_soc > 19.0:
            warn_msg = "Achtung, Batteriestand unter 20 Prozent! Bitte nächste Ladesäule einplanen."
            self.bot.send_message(f"🔋 {warn_msg}")
            speak(warn_msg)

    def check_zoll_for_destination(self, destination):
        dest_lower = destination.lower()
        # Erweiterte Liste für die Schweiz und Grenzregionen
        swiss_keywords = ["schweiz", "olten", "wangen", "zürich", "schaffhausen", "kreuzlingen", "basel", "bern", "luzern", "st. gallen", "zoll", "frauenfeld", "winterthur"]
        
        if any(keyword in dest_lower for keyword in swiss_keywords):
            info = "⚠️ GRENZÜBERTRITT SCHWEIZ! Zollpapiere, Frachtbrief & LSVA-Maut bereitstellen."
            dashboard_data["zoll_info"] = info
            self.bot.send_message(f"🛃 {info}")
            speak("Achtung, Grenzüberschreitung in die Schweiz. Bitte Zollpapiere bereithalten.")
        else:
            dashboard_data["zoll_info"] = "Kein Zoll erforderlich (Inland / Deutschland)."

    def handle_pause_response(self, text):
        text = text.strip().lower()
        if text == "/ja":
            msg = "Pause registriert. Lenkzeit pausiert."
            self.bot.send_message(f"✅ {msg}")
            speak(msg)
            return True
        elif text == "/nein":
            msg = "Wird als Arbeitszeit gewertet."
            self.bot.send_message(f"🛠️ {msg}")
            speak(msg)
            return True
        return False
