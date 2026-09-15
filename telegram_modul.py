import urllib.request
import urllib.parse

# Feste Zugangsdaten für deinen E-LKW-Tracker
TELEGRAM_BOT_TOKEN = "8413301731:AAGMlffH8VYDjCUzC_UMewy0G-hau7sK8Ao"
TELEGRAM_CHAT_ID = "8941361378"

def sende_telegram_nachricht(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        daten = urllib.parse.urlencode({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=daten, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                print(f"[Telegram Fehler]: HTTP Status {response.status}")
    except Exception as e:
        print(f"[Telegram Fehler]: {e}")
