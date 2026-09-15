import osmium
import sys

class RoadNetworkHandler(osmium.SimpleHandler):
    def __init__(self):
        super(RoadNetworkHandler, self).__init__()
        self.node_count = 0
        self.way_count = 0

    def node(self, n):
        self.node_count += 1

    def way(self, w):
        if 'highway' in w.tags:
            self.way_count += 1

def analyze_map(file_path):
    print(f"Lese Map ein: {file_path} ...")
    handler = RoadNetworkHandler()
    handler.apply_file(file_path, locations=True)
    print(f"Gefundene Knoten: {handler.node_count}")
    print(f"Gefundene Straßen-Wege: {handler.way_count}")

if __name__ == "__main__":
    map_file = "maps/baden-wuerttemberg-latest.osm.pbf"
    analyze_map(map_file)
