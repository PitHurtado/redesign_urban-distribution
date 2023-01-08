import pandas as pd
import folium
from branca.element import Figure
import branca.colormap as cm
from classes import Customer, Satelite

class DrawingMap:
    def __init__(self,
                 location: list[float],
                 ):
        self.map = folium.Map(location=location, zoom_start=12)
        self.fig = Figure(width=1000, height=600)
        self.fig.add_child(self.map)
        self.linear = None

    def setHue(self, minLabel: int, maxLabel: int, colors=["blue", "yellow", "red"]):
        self.linear = cm.LinearColormap(colors, vmin=minLabel, vmax=maxLabel)
        return self.linear

    def addNodes(self, df: pd.DataFrame, radius=3, fill=True, color='blue'):
        if self.linear is not None:
            for row in df.itertuples():
                folium.CircleMarker(
                    location=[row.lat, row.lon],
                    radius=radius,
                    fill=fill,
                    color=self.linear(row.label),
                    leyend_name = "label"
                ).add_to(self.map)
            self.map.add_child(self.linear)
        else:
            for row in df.itertuples():
                folium.CircleMarker(
                    location=[row.lat, row.lon],
                    radius=radius,
                    fill=fill,
                    color=color,
                ).add_to(self.map)

    def addCustomers(self, list_customers: list[Customer], label: str, radius=1, fill=True, color='blue'):
        if self.linear is not None:
            for s in list_customers:
                folium.CircleMarker(
                    location=[s.lat, s.lon],
                    radius=radius,
                    fill=fill,
                    color=self.linear(s.__dict__[label]),
                    leyend_name = label
                ).add_to(self.map)
            self.map.add_child(self.linear)
        else:
            for s in list_customers:
                folium.CircleMarker(
                    location=[s.lat, s.lon],
                    radius=radius,
                    fill=fill,
                    color=color,
                ).add_to(self.map)

    def addCircles(self, df: pd.DataFrame, radius = 8_000):
        for row in df.itertuples():
            folium.Circle(
                location=[row.lat, row.lon],
                radius=radius,
                fill = True,
                color='#B22222'
            ).add_to(self.map)

    def viewMap(self):
        return self.map

