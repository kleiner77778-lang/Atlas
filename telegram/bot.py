import urllib.request
import urllib.parse
import json

TELEGRAM_TOKEN = "8413301731:AAHRM32xA2CkAkrrcf85sqYDR88YK14k3bs"
CHAT_ID = "8941361378"

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": message}).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"[Telegram Fehler]: {e}")

def get_telegram_updates(offset=None):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?timeout=2"
        if offset:
            url += f"&offset={offset}"
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, timeout=3)
        data = json.loads(response.read().decode("utf-8"))
        if data.get("ok"):
            return data.get("result", [])
    except Exception:
        pass
    return []
