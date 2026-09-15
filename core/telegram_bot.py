import urllib.request
import urllib.parse

TELEGRAM_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
TELEGRAM_CHAT_ID = "8941361378"

def send_telegram_message(message):
    """
    Sendet die Fahrtdaten und Stau-Warnungen direkt über die Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                print(f"[ERROR] Telegram API Fehler: Status {response.status}")
    except Exception as e:
        print(f"[ERROR] Konnte Telegram-Nachricht nicht senden: {e}")
