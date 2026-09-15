class StromChecker:
    def __init__(self, warn_schwelle_km=100.0):
        self.warn_schwelle_km = warn_schwelle_km
        self.alarm_gesendet = False

    def pruefe_batterie(self, rest_km, telegram_callback):
        if rest_km <= self.warn_schwelle_km and not self.alarm_gesendet:
            alarm_text = (
                f"🔋 *BATTERIE-WARNUNG (E-Lkw)*\n"
                f"Restreichweite unter {int(self.warn_schwelle_km)} km erreicht! "
                f"(Aktuell noch ca. {rest_km:.1f} km übrig).\n"
                f"👉 Bitte Ladesäule einplanen!"
            )
            telegram_callback(alarm_text)
            self.alarm_gesendet = True

    def reset(self):
        self.alarm_gesendet = False
