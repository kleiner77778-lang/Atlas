import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

from gps.tracker import get_phone_gps
from traffic.detector import TrafficDetector
from sound.alarm import trigger_loud_alarm
from telegram.bot import send_telegram_message, get_telegram_updates
from report.daily_report import ShiftReport

class AtlasAppUI(BoxLayout):
    def __init__(self, **kwargs):
        super(AtlasAppUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        self.traffic_detector = TrafficDetector()
        self.shift_reporter = ShiftReport()
        self.tracking_active = False
        self.target_destination = "Nicht gesetzt"

        # Titel
        self.add_widget(Label(text="[b]Atlas Lkw-Tracker[/b]", markup=True, font_size=24, size_hint_y=None, height=50))

        # Status Anzeige
        self.status_label = Label(text="Status: Bereit", font_size=18, size_hint_y=None, height=40)
        self.add_widget(self.status_label)

        # Ziel Eingabe
        self.dest_input = TextInput(text='', hint_text='Ziel eingeben (z.B. Zürich)', multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.dest_input)

        self.set_dest_btn = Button(text="Ziel übernehmen", size_hint_y=None, height=50)
        self.set_dest_btn.bind(on_press=self.set_destination_action)
        self.add_widget(self.set_dest_btn)

        # Start / Stop Buttons
        self.start_btn = Button(text="SCHICHT STARTEN", background_color=(0, 0.7, 0, 1), size_hint_y=None, height=60)
        self.start_btn.bind(on_press=self.start_shift_action)
        self.add_widget(self.start_btn)

        self.stop_btn = Button(text="SCHICHT BEENDEN", background_color=(0.8, 0, 0, 1), size_hint_y=None, height=60)
        self.stop_btn.bind(on_press=self.stop_shift_action)
        self.add_widget(self.stop_btn)

        # Live Info Box
        self.info_label = Label(text="KM: 0.0 | kWh: 0.0 | Speed: 0.0 km/h", font_size=16)
        self.add_widget(self.info_label)

        # Hintergrund-Threads starten
        threading.Thread(target=self.background_worker, daemon=True).start()
        threading.Thread(target=self.telegram_listener, daemon=True).start()

    def set_destination_action(self, instance):
        if self.dest_input.text.strip():
            self.target_destination = self.dest_input.text.strip()
            send_telegram_message(f"🎯 Neues Ziel gesetzt: {self.target_destination}")
            self.status_label.text = f"Ziel: {self.target_destination}"

    def start_shift_action(self, instance):
        self.shift_reporter.start_shift()
        self.traffic_detector.reset_border()
        self.tracking_active = True
        self.status_label.text = "Status: Schicht aktiv 🚀"
        send_telegram_message(f"🚀 Schicht & Tracking gestartet!\n📍 Ziel: {self.target_destination}")

    def stop_shift_action(self, instance):
        if self.tracking_active:
            report = self.shift_reporter.get_shift_report()
            send_telegram_message(f"🛑 Schicht beendet!\n\n{report}")
            self.tracking_active = False
            self.status_label.text = "Status: Schicht beendet"

    def background_worker(self):
        """Hauptschleife für GPS, Stau und Pausen im Hintergrund"""
        while True:
            if self.tracking_active:
                gps_data = get_phone_gps()
                if gps_data and gps_data["latitude"] and gps_data["longitude"]:
                    lat = gps_data["latitude"]
                    lon = gps_data["longitude"]
                    speed = gps_data["speed"]

                    metrics = self.shift_reporter.update_metrics(lat, lon, speed)
                    
                    # UI Live-Update über Kivy Clock sicher aufrufen
                    Clock.schedule_once(lambda dt: self.update_ui_text(metrics, speed))

                    # Grenzübertritt prüfen
                    border_msg = self.traffic_detector.check_border_crossing(lat)
                    if border_msg:
                        send_telegram_message(border_msg)
                        trigger_loud_alarm("Achtung! Landesgrenze überschritten. Papiere und Maut beachten!")
                    
                    # Stau prüfen
                    traffic = self.traffic_detector.check_traffic(speed, lat, lon)
                    if traffic["alert"]:
                        send_telegram_message(traffic["message"])
                        trigger_loud_alarm("Achtung Stau Gefahr! Bitte Umfahrung prüfen!")
                    
                    # Pause prüfen
                    pause_msg = self.shift_reporter.check_pause(speed)
                    if pause_msg:
                        send_telegram_message(pause_msg)

            time.sleep(10)

    def update_ui_text(self, metrics, speed):
        self.info_label.text = f"KM: {metrics['odometer_km']} | kWh: {metrics['energy_kwh']} | Speed: {round(speed, 1)} km/h"

    def telegram_listener(self):
        """Horcht parallel auf Telegram-Befehle wie /start, /ende, /ziel"""
        last_update_id = 0
        while True:
            updates = get_telegram_updates(last_update_id + 1)
            for update in updates:
                last_update_id = update.get("update_id", last_update_id)
                message = update.get("message", {})
                text = message.get("text", "").strip()
                
                if text.startswith("/start"):
                    Clock.schedule_once(lambda dt: self.start_shift_action(None))
                elif text.startswith("/stop") or text.startswith("/ende"):
                    Clock.schedule_once(lambda dt: self.stop_shift_action(None))
                elif text.startswith("/ziel"):
                    parts = text.split(maxsplit=1)
                    if len(parts) > 1:
                        self.target_destination = parts[1]
                        Clock.schedule_once(lambda dt: self.set_destination_action(None))
                elif text in ["/status", "/tacho", "/kontingent"]:
                    metrics = self.shift_reporter.get_current_metrics()
                    send_telegram_message(f"📊 Aktueller Tacho:\n- Kilometer: {metrics['odometer_km']} km\n- Energie: {metrics['energy_kwh']} kWh\n- Ziel: {self.target_destination}")
            time.sleep(2)

class AtlasApp(App):
    def build(self):
        return AtlasAppUI()

if __name__ == '__main__':
    AtlasApp().run()
