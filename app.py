import json
import urllib.request
import urllib.parse
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MAP_SWITZERLAND = "/data/data/com.termux/files/home/Atlas/maps/switzerland-latest.osm.pbf"
MAP_GERMANY = "/data/data/com.termux/files/home/Atlas/maps/baden-wuerttemberg-latest.osm.pbf"

VEHICLES = {
    "Volvo FM Electric (18t)": {"consumption": 95.0, "max_range": 300},
    "Standard PKW": {"consumption": 18.0, "max_range": 600}
}

def get_coordinates(ziel_name):
    try:
        encoded_query = urllib.parse.quote(ziel_name)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1&countrycodes=de,ch"
        req = urllib.request.Request(url, headers={'User-Agent': 'AtlasNavi/1.0'})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            results = json.loads(response.read().decode())
            if results:
                return float(results[0]['lon']), float(results[0]['lat'])
    except Exception as e:
        print("Geocoding-Hinweis:", e)
    return None, None

def calculate_atlas_route(start_coords, dest_coords):
    start_lon, start_lat = start_coords
    dest_lon, dest_lat = dest_coords

    dist_check = ((dest_lon - start_lon)**2 + (dest_lat - start_lat)**2)**0.5 * 111000
    if dist_check < 150:
        return {
            "distance_km": 0.0,
            "duration_min": 0,
            "geometry": {
                "type": "LineString", 
                "coordinates": [[start_lon, start_lat], [dest_lon, dest_lat]]
            },
            "source": "Ziel erreicht"
        }

    # Echtes Straßen-Routing über OSRM
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{dest_lon},{dest_lat}?overview=full&geometries=geojson"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AtlasNavi/1.0'})
        with urllib.request.urlopen(req, timeout=5.0) as response:
            data = json.loads(response.read().decode())
            if data.get("code") == "Ok":
                route = data["routes"][0]
                return {
                    "distance_km": round(route["distance"] / 1000, 2),
                    "duration_min": round(route["duration"] / 60, 1),
                    "geometry": route["geometry"],
                    "source": "Online (Straßen-Routing)"
                }
    except Exception as e:
        print("OSRM-Fehler:", e)

    # Fallback Luftlinie
    return {
        "distance_km": round(dist_check / 1000, 2),
        "duration_min": max(1, round((dist_check / 1000) * 2, 0)),
        "geometry": {
            "type": "LineString",
            "coordinates": [[start_lon, start_lat], [dest_lon, dest_lat]]
        },
        "source": "Offline-Fallback (Luftlinie)"
    }

@app.route('/')
def index():
    return render_template('index.html', vehicles=VEHICLES)

@app.route('/api/route')
def api_route():
    try:
        ziel = request.args.get('ziel', '')
        lat_str = request.args.get('lat')
        lon_str = request.args.get('lon')

        if not ziel:
            return jsonify({"status": "error", "message": "Kein Ziel angegeben."})
        if not lat_str or not lon_str:
            return jsonify({"status": "error", "message": "Kein Startpunkt (GPS/Klick) vorhanden."})

        ziel_lon, ziel_lat = get_coordinates(ziel)
        if ziel_lon is None or ziel_lat is None:
            return jsonify({"status": "error", "message": "Ziel konnte nicht gefunden werden."})

        start_lat = float(lat_str)
        start_lon = float(lon_str)

        route_data = calculate_atlas_route((start_lon, start_lat), (ziel_lon, ziel_lat))

        return jsonify({
            "status": "success",
            "ziel_ort": ziel,
            "ziel_lat": ziel_lat,
            "ziel_lon": ziel_lon,
            "distance_km": route_data['distance_km'],
            "duration_min": route_data['duration_min'],
            "geojson": route_data['geometry'],
            "routing_mode": route_data['source']
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
