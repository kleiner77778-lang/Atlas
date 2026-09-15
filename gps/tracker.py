import subprocess
import json

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
