class OfflineNaviEngine:
    def __init__(self, vehicle_config, telegram_bot=None):
        self.vehicle = vehicle_config
        self.bot = telegram_bot
        print(f"[NaviEngine] Initialisiert für {self.vehicle.get('name')}")

    def calculate_route(self, start, destination):
        print(f"[NaviEngine] Berechne gewichtsbasierten Lkw-Pfad von '{start}' nach '{destination}'...")
        
        # Simulierte Werte für die Route
        distance = 42.5
        energy = 75.0
        
        # Wenn der Bot da ist, Fahrt protokollieren
        if self.bot:
            self.bot.log_trip(start, destination, distance, energy)
            
        return {"status": "Route berechnet", "distance_km": distance, "energy_est_kwh": energy}
