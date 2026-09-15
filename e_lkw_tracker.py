import os
import time
from core.tracker_logic import load_vehicle_config
from core.telegram_bot import TelegramBotManager
from core.dashboard_ui import start_dashboard_thread, speak

def main():
    print("==================================================")
    print(" ATLAS - COCKPIT, SPRACHAUSGABE & LIVE-FENSTER  ")
    print("==================================================")
    
    vehicle = load_vehicle_config()
    
    # 1. Startet das Live-Fenster (Web-Dashboard auf Port 5000)
    start_dashboard_thread()
    
    bot = TelegramBotManager()
    
    print(f"Fahrzeug: {vehicle.get('name')}")
    print("System aktiv. Sprachausgabe & Dashboard online.")
    
    bot.send_message("🟢 Atlas E-Lkw Cockpit online.\n- Sprachausgabe aktiv\n- Live-Fenster unter http://localhost:5000")
    speak("System gestartet. Bereit für die Tour.")
    
    try:
        while True:
            bot.poll_commands()
            
            if bot.active_shift:
                # Simulation der Telematik (Geschwindigkeit & Strecke)
                simulated_speed = 45.0  
                simulated_distance_delta = 0.04  
                bot.tacho_manager.update_telematics(simulated_speed, simulated_distance_delta)
                
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[System] Beendet.")
        speak("System heruntergefahren.")
        bot.send_message("🔴 System heruntergefahren.")

if __name__ == "__main__":
    main()
