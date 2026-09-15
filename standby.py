import os
import time

# ==========================================
# ATLAS STANDBY-GUARD (BIS EOF)
# ==========================================

def warte_auf_start():
    """
    Sorgt dafür, dass das System absolut im Standby bleibt 
    und keine Hintergrundprozesse oder GPS-Daten erfasst,
    bis die Lock-Datei ('atlas_active.lock') manuell erstellt wird.
    """
    start_flag = "atlas_active.lock"
    
    print("--- ATLAS TRACKER: STANDBY MODUS ---")
    print(f"Warte auf Start-Signal ({start_flag})...")
    
    # Warteschleife blockiert den Start, bis die Lock-Datei existiert
    while not os.path.exists(start_flag):
        time.sleep(2)
        
    print(">>> Start-Signal da! System wird hochgefahren...")

# ==========================================
# END OF FILE (EOF)
# ==========================================

