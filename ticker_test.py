import subprocess
import time

def update_notification(title, content):
    subprocess.run([
        "termux-notification",
        "--id", "elkw_ticker",
        "--title", title,
        "--content", content,
        "--ongoing"
    ])

print("Live-Ticker Test läuft im Hintergrund...")

for i in range(1, 10):
    rest_akku = 85 - i
    eta = f"14:{30 + i}"
    
    title = f"E-Lkw Ticker | Akku: {rest_akku}%"
    content = f"Ziel: Depot | ETA: {eta} | Distanz: {12 - i} km"
    
    update_notification(title, content)
    time.sleep(5)

print("Test beendet.")
