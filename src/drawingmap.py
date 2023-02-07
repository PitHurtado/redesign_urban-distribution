import folium
import branca.colormap as cm
from branca.element import Figure
from src.classes import Locatable


class DrawingMap:
    def __init__(self,
                 location: list[float],
                 style: str = 'cartodbpositron'
                 ):
        self.map = folium.Map(location=location, zoom_start=12)
        self.fig = Figure(width=800, height=600)
        self.fig.add_child(self.map)
        self.linear = None
        # folium.TileLayer(style).add_to(self.map)

    def setHue(self, minLabel: int, maxLabel: int, colors=["blue", "yellow", "red"]):
        self.linear = cm.LinearColormap(colors, vmin=minLabel, vmax=maxLabel)
        return self.linear

    def addNode(self, location, radius=1, fill=True, color='blue'):
        folium.CircleMarker(
            location=location,
            radius=radius,
            fill=fill,
            color=color
        ).add_to(self.map)

    def addNodes(self, list_locatables: list[Locatable], radius=1, fill=True, color='blue'):
        for obj in list_locatables:
            self.addNode(location=(obj.lat, obj.lon),
                         radius=radius,
                         fill=fill,
                         color=color)

    def addMarker(self, location, label: str):
        folium.Marker(
            location=location,
            popup=label,
        ).add_to(self.map)

    def viewMap(self):
        return self.map
