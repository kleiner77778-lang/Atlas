import tkinter as tk
import time
import threading
import subprocess

def speak(text):
    clean_text = text.replace("🔋", "Akku").replace("🎯", "Ziel").replace("ETA:", "Ankunftszeit").replace("📍", "Distanz")
    subprocess.run(["termux-tts-speak", clean_text])

class LiveTickerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E-Lkw Ticker")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.geometry("500x65+40+40")
        self.root.configure(bg="#111111")
        
        self.label = tk.Label(
            self.root, 
            text="E-Lkw Ticker bereit...", 
            font=("Arial", 13, "bold"), 
            fg="#00FF66", 
            bg="#111111"
        )
        self.label.pack(expand=True, fill="both", padx=10, pady=5)
        self.root.bind("<Button-1>", lambda e: self.root.destroy())

    def update_data(self):
        i = 0
        while True:
            # Hier empfängt das Overlay die Daten (vorerst simuliert oder per Datei/Schnittstelle)
            rest_akku = 85 - (i % 20)
            eta = f"14:{30 + (i % 30):02d}"
            distanz = 12 - (i % 10)
            
            text = f"🔋 SoC: {rest_akku}% | 🎯 Ziel | ETA: {eta} | 📍 {distanz}km"
            
            try:
                self.root.after(0, lambda t=text: self.label.config(text=t))
                threading.Thread(target=speak, args=(text,), daemon=True).start()
            except:
                break
                
            i += 1
            time.sleep(10)

    def run(self):
        threading.Thread(target=self.update_data, daemon=True).start()
        self.root.mainloop()

if __name__ == "__main__":
    app = LiveTickerApp()
    app.run()
