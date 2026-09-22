import os
import random
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.utils import platform

# --- PYJNIUS GPS IMPLEMENTIERUNG ---
if platform == 'android':
    from jnius import PythonJavaClass, java_method, autoclass

    class GPSListener(PythonJavaClass):
        __javainterfaces__ = ['android/location/LocationListener']
        __javacontext__ = 'app'

        def __init__(self, callback):
            super(GPSListener, self).__init__()
            self.callback = callback

        @java_method('(Landroid/location/Location;)V')
        def onLocationChanged(self, location):
            if location:
                lat = location.getLatitude()
                lon = location.getLongitude()
                speed = location.getSpeed() * 3.6  # m/s in km/h
                self.callback(lat, lon, speed)

        @java_method('(Ljava/lang/String;ILandroid/os/Bundle;)V')
        def onStatusChanged(self, provider, status, extras):
            pass

        @java_method('(Ljava/lang/String;)V')
        def onProviderEnabled(self, provider):
            pass

        @java_method('(Ljava/lang/String;)V')
        def onProviderDisabled(self, provider):
            pass

    class GPSRunnable(PythonJavaClass):
        __javainterfaces__ = ['java/lang/Runnable']
        __javacontext__ = 'app'

        def __init__(self, lm, listener):
            super(GPSRunnable, self).__init__()
            self.lm = lm
            self.listener = listener

        @java_method('()V')
        def run(self):
            try:
                self.lm.requestLocationUpdates(
                    'gps', 1000, 1, self.listener
                )
            except Exception as e:
                print(f"Error registering GPS: {e}")


# --- MATRIX REGEN BACKGROUND ---
class MatrixRainWidget(Widget):
    def __init__(self, **kwargs):
        super(MatrixRainWidget, self).__init__(**kwargs)
        self.columns = []
        self.bind(size=self._setup_matrix, pos=self._setup_matrix)
        Clock.schedule_interval(self.update_matrix, 0.05)

    def _setup_matrix(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)

        col_width = 20
        num_cols = int(self.width / col_width) + 1 if self.width > 0 else 10
        self.columns = []

        for i in range(num_cols):
            self.columns.append({
                'x': self.x + (i * col_width),
                'y': random.randint(0, int(self.height) if self.height > 0 else 800),
                'speed': random.randint(5, 15),
                'length': random.randint(5, 15)
            })

    def update_matrix(self, dt):
        self.canvas.clear()
        with self.canvas:
            for col in self.columns:
                col['y'] -= col['speed']
                if col['y'] < 0:
                    col['y'] = self.height + random.randint(10, 100)
                    col['speed'] = random.randint(5, 15)

                # Matrix-Regentropfen zeichnen
                Color(0, 1, 0, 0.35)
                for j in range(col['length']):
                    py = col['y'] + (j * 15)
                    if 0 <= py <= self.height:
                        Rectangle(pos=(col['x'], py), size=(4, 10))


# --- HAUPTLAYOUT ---
class MainScreen(FloatLayout):
    pass


# --- KIVY INTERFACE BUILDER ---
KV = '''
<MainScreen>:
    MatrixRainWidget:
        id: matrix_bg

    # ZENTRALER BILDERBEREICH
    BoxLayout:
        orientation: 'vertical'
        size_hint: (0.9, 0.6)
        pos_hint: {'center_x': 0.5, 'center_y': 0.55}
        spacing: 15

        Label:
            text: "ATLAS TRACKER"
            font_size: '22sp'
            bold: True
            color: (0, 1, 0, 1)
            size_hint_y: None
            height: 30

        Label:
            text: app.speed_text
            font_size: '64sp'
            bold: True
            color: (1, 1, 1, 1)

        Label:
            text: app.range_text
            font_size: '18sp'
            color: (0.8, 0.8, 0.8, 1)

        Label:
            text: app.gps_status
            font_size: '12sp'
            color: (1, 0.3, 0.3, 1) if "Fehler" in app.gps_status else (0, 0.8, 0, 1)
            size_hint_y: None
            height: 20

        Label:
            text: app.coords_text
            font_size: '14sp'
            color: (0.6, 0.6, 0.6, 1)
            size_hint_y: None
            height: 30

    # MENÜ BUTTON UNTEN RECHTS
    Button:
        text: "≡"
        font_size: '24sp'
        bold: True
        background_normal: ''
        background_color: (0, 0, 0, 0.6)
        color: (0, 1, 0, 1)
        size_hint: (None, None)
        size: (50, 50)
        pos_hint: {'right': 0.95, 'y': 0.03}
        on_press: app.open_menu()
'''


class AtlasApp(App):
    speed_text = StringProperty("0 km/h")
    range_text = StringProperty("Restreichweite: ~511 km")
    coords_text = StringProperty("Lat: -- | Lon: --")
    gps_status = StringProperty("GPS wird initialisiert...")

    def build(self):
        Builder.load_string(KV)
        return MainScreen()

    def on_start(self):
        Clock.schedule_once(self.start_gps, 1)

    def start_gps(self, dt):
        if platform == 'android':
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')

                activity = PythonActivity.mActivity
                self.location_manager = activity.getSystemService(Context.LOCATION_SERVICE)
                self.gps_listener = GPSListener(self.update_gps_ui)

                # Execute GPS updates inside Android's UI thread
                runnable = GPSRunnable(self.location_manager, self.gps_listener)
                activity.runOnUiThread(runnable)

                self.gps_status = "GPS aktiv"
            except Exception as e:
                self.gps_status = f"GPS-Fehler: {str(e)}"
        else:
            self.gps_status = "Desktop-Modus (Simulation)"
            Clock.schedule_interval(self._simulate_speed, 2)

    def update_gps_ui(self, lat, lon, speed):
        self.speed_text = f"{int(speed)} km/h"
        self.coords_text = f"Lat: {lat:.4f} | Lon: {lon:.4f}"
        self.gps_status = "GPS Empfang OK"

    def _simulate_speed(self, dt):
        sim_speed = random.randint(40, 85)
        self.speed_text = f"{sim_speed} km/h"
        self.coords_text = "Lat: 47.7606 | Lon: 8.8394"

    def open_menu(self):
        print("Menü geöffnet")


if __name__ == '__main__':
    AtlasApp().run()
