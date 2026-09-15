import os
import json
import osmium

class TruckNetworkHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.nodes = 0
        self.ways = 0

    def node(self, n):
        self.nodes += 1

    def way(self, w):
        if 'highway' in w.tags:
            self.ways += 1

def load_vehicle_config():
    config_path = "config/vehicle.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {"name": "Volvo FM Electric"}
