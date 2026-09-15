import time
import json
import subprocess
from core.nav_backend import NavBackend
from core.telegram_bot import send_telegram_message, get_telegram_updates

def get_phone_gps():
    try:
        result = subprocess.run(
            ["termux-location", "-p", "gps"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            return {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "speed": data.get("speed", 0.0) * 3.6
            }
    except Exception:
        pass
    return None

def trigger_loud_alarm(text="Achtung! Verkehrshinweis prüfen."):
    try:
        subprocess.run(["termux-volume", "stream", "15"], capture_output=True)
        subprocess.run(["termux-tts-speak", text], capture_output=True)
    except Exception:
        pass

def main():
    print("[INFO] Atlas Lkw-System mit Grenz- und Schichtüberwachung aktiv...")
    backend = NavBackend()
    
    tracking_active = False
    target_destination = "Nicht gesetzt"
    last_update_id = 0
    
    send_telegram_message("🚛 Atlas Lkw-Tracker bereit.\nBefehle: /start, /ziel <Ort>, /status, /ende")
    
    try:
        while True:
            # 1. Telegram-Befehle abrufen
            updates = get_telegram_updates(last_update_id + 1)
            for update in updates:
                last_update_id = update.get("update_id", last_update_id)
                message = update.get("message", {})
                text = message.get("text", "").strip()
                
                if text.startswith("/start"):
                    backend.start_shift()
                    tracking_active = True
                    send_telegram_message(f"🚀 Schicht & Tracking gestartet!\n📍 Ziel: {target_destination}")
                
                elif text.startswith("/stop") or text.startswith("/ende"):
                    if tracking_active:
                        report = backend.get_shift_report()
                        send_telegram_message(f"🛑 Schicht beendet!\n\n{report}")
                        tracking_active = False
                    else:
                        send_telegram_message("⚠️ Es lief keine aktive Schicht.")
                
                elif text.startswith("/ziel"):
                    parts = text.split(maxsplit=1)
                    if len(parts) > 1:
                        target_destination = parts[1]
                        send_telegram_message(f"🎯 Neues Ziel gesetzt: {target_destination}")
                    else:
                        send_telegram_message("⚠️ Bitte gib ein Ziel an, z.B. `/ziel Zürich`")
                
                elif text in ["/status", "/tacho", "/kontingent"]:
                    metrics = backend.get_current_metrics()
                    send_telegram_message(f"📊 Aktueller Tacho:\n- Kilometer: {metrics['odometer_km']} km\n- Energie: {metrics['energy_kwh']} kWh\n- Ziel: {target_destination}\n- Status: {'Aktiv' if tracking_active else 'Bereit'}")

            # 2. GPS, Stau & Grenzübertritt bei aktivem Tracking
            if tracking_active:
                gps_data = get_phone_gps()
                if gps_data and gps_data["latitude"] and gps_data["longitude"]:
                    lat = gps_data["latitude"]
                    lon = gps_data["longitude"]
                    speed = gps_data["speed"]

                    metrics = backend.update_metrics(lat, lon, speed)
                    
                    # Grenzübertritt prüfen
                    border_msg = backend.check_border_crossing(lat, lon)
                    if border_msg:
                        send_telegram_message(border_msg)
                        # Sofortiger lauter akustischer Alarm mit Sprachansage
                        trigger_loud_alarm("Achtung! Landesgrenze überschritten. Papiere und Maut beachten!")
                    
                    # Stau prüfen
                    traffic = backend.check_traffic(speed, lat, lon)
                    if traffic["alert"]:
                        send_telegram_message(traffic["message"])
                        trigger_loud_alarm("Achtung Stau Gefahr! Bitte Umfahrung prüfen!")
                    
                    # Pause prüfen
                    pause_msg = backend.check_pause(speed)
                    if pause_msg:
                        send_telegram_message(pause_msg)
                
            time.sleep(10)
    except KeyboardInterrupt:
        print("[INFO] System gestoppt.")

if __name__ == "__main__":
    main()
