import sys
import os

# Hauptverzeichnis zum Python-Pfad hinzufügen, damit core/ gefunden wird
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import threading
import time

from core.nav_backend import NavBackend
from core.telegram_bot import send_telegram_message
from core.overlay_hud import get_phone_gps

class AtlasAppUI(BoxLayout):
    def __init__(self, **kwargs):
        super(AtlasAppUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20

        # Titel
        self.add_widget(Label(text='[b]Atlas Truck Tracker[/b]', markup=True, font_size='24sp', size_hint=(1, 0.15)))

        # Live-Metrik-Anzeige
        self.metrics_label = Label(text='KM: 0.0 | kWh: 0.0\nSpeed: 0.0 km/h', font_size='18sp', size_hint=(1, 0.3), halign='center', valign='middle')
        self.metrics_label.bind(size=self.metrics_label.setter('text_size'))
        self.add_widget(self.metrics_label)

        # Status / Verkehr / Pause Anzeige
        self.status_label = Label(text='Status: Bereit', font_size='16sp', size_hint=(1, 0.3), halign='center', valign='middle')
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.add_widget(self.status_label)

        # Steuerungs-Button
        self.btn = Button(text='Tracking starten', font_size='18sp', size_hint=(1, 0.25))
        self.btn.bind(on_press=self.toggle_tracking)
        self.add_widget(self.btn)

        self.is_running = False
        self.backend = NavBackend()
        self.thread = None

    def toggle_tracking(self, instance):
        if not self.is_running:
            self.is_running = True
            self.btn.text = 'Tracking stoppen'
            self.status_label.text = 'Status: Läuft aktiv...'
            send_telegram_message("🚀 Atlas App-Tracking wurde gestartet.")
            
            # Tracking-Loop im Hintergrund-Thread starten
            self.thread = threading.Thread(target=self.tracking_loop, daemon=True)
            self.thread.start()
        else:
            self.is_running = False
            self.btn.text = 'Tracking starten'
            self.status_label.text = 'Status: Gestoppt'
            send_telegram_message("🛑 Atlas App-Tracking wurde gestoppt.")

    def tracking_loop(self):
        while self.is_running:
            gps_data = get_phone_gps()
            
            if gps_data and gps_data["latitude"] and gps_data["longitude"]:
                metrics = self.backend.update_metrics(
                    gps_data["latitude"], 
                    gps_data["longitude"], 
                    gps_data["speed"]
                )
                traffic = self.backend.check_traffic(gps_data["speed"])
                
                # Telegram Update senden
                msg = f"KM: {metrics['odometer_km']} | kWh: {metrics['energy_kwh']} | Speed: {metrics['speed_kmh']} km/h | {traffic['message']}"
                send_telegram_message(msg)
                
                # Prüfen auf 15-Minuten-Pause
                pause_msg = self.backend.check_pause(gps_data["speed"])
                if pause_msg:
                    send_telegram_message(pause_msg)
                    
                # UI-Aktualisierung thread-sicher über Clock aufrufen
                Clock.schedule_once(lambda dt: self.update_ui_texts(metrics, traffic))
                
            time.sleep(10)

    def update_ui_texts(self, metrics, traffic):
        self.metrics_label.text = f"KM: {metrics['odometer_km']} | kWh: {metrics['energy_kwh']}\nSpeed: {metrics['speed_kmh']} km/h"
        self.status_label.text = f"Verkehr: {traffic['message']}"

class AtlasApp(App):
    def build(self):
        return AtlasAppUI()

if __name__ == '__main__':
    AtlasApp().run()
