import threading
from flask import Flask, render_template_string
from audio.speech_engine import speak

app = Flask(__name__)

# Globale Telematik-Daten für das Live-Fenster
dashboard_data = {
    "contingent": "Keines",
    "tacho": 0.0,
    "driving_mins": 0,
    "battery_soc": 85.0,
    "battery_kwh": 459.0,
    "destination": "Kein Ziel",
    "status": "Bereit",
    "zoll_info": "Keine aktiven Zoll-Meldungen"
}

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Volvo FM Electric - Cockpit</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="3">
        <style>
            body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            .card { background: #1e1e1e; border-radius: 12px; padding: 15px; margin: 10px auto; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            h1 { font-size: 20px; color: #ff9800; }
            .val { font-size: 24px; font-weight: bold; color: #4caf50; }
            .zoll { background: #311b92; border-left: 5px solid #7c4dff; padding: 10px; margin-top: 10px; text-align: left; }
        </style>
    </head>
    <body>
        <h1>Volvo FM Electric - Live Cockpit</h1>
        <div class="card">
            <p>Kontingent & Status:<br><span class="val" id="status">{{ data.contingent }} ({{ data.status }})</span></p>
            <p>Tacho-Stand:<br><span class="val">{{ "%.1f"|format(data.tacho) }} km</span></p>
            <p>Lenkzeit:<br><span class="val">{{ data.driving_mins }} Min</span></p>
            <p>Batterie (SoC):<br><span class="val">{{ data.battery_soc }}% ({{ data.battery_kwh }} kWh)</span></p>
            <p>Ziel:<br><span class="val" id="dest">{{ data.destination }}</span></p>
            <div class="zoll">
                <strong>🛃 Zoll- & Grenzhinweis:</strong><br>
                <span>{{ data.zoll_info }}</span>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, data=dashboard_data)

def run_web_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def start_dashboard_thread():
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()
    print("[Dashboard] Live-Fenster läuft unter http://localhost:5000")
