import pandas as pd
import folium
import matplotlib.pyplot as plt
from branca.element import Figure
import branca.colormap as cm
from matplotlib import style

style.use('ggplot') or plt.style.use('ggplot')


class DrawingMap:
    def __init__(self,
                 location: list[float],
                 ):
        self.map = folium.Map(location=location, zoom_start=12)
        self.fig = Figure(width=800, height=600)
        self.fig.add_child(self.map)
        self.linear = None

    def setHue(self, minLabel: int, maxLabel: int, colors=["blue", "yellow", "red"]):
        self.linear = cm.LinearColormap(colors, vmin=minLabel, vmax=maxLabel)
        return self.linear

    def addNodes(self, df: pd.DataFrame, radius=3, fill=True):
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
                    color='blue',
                ).add_to(self.map)

    def viewMap(self):
        return self.map

# %%
