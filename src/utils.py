import json
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from classes import Satellite, Cluster, Vehicle


class LoadingData:
    @staticmethod
    def load_satellites(DEBUG: bool = False) -> tuple[dict[str, Satellite], pd.DataFrame]:
        satellites = {}
        df = pd.read_csv('../others/Levantamiento de Información/base_satellites.csv')
        for i in range(len(df)):
            id_s = str(df.nombre[i])
            new_satellite = Satellite(id_s=id_s
                                      , lon=df.longitud[i]
                                      , lat=df.latitud[i]
                                      , distanceFromDC=df.loc[i, 'distance.value'] / 1000
                                      , durationFromDC=df.loc[i, 'duration.value'] / 3600
                                      , durationInTrafficFromDC=df.loc[i, 'duration_in_traffic.value'] / 3600
                                      , costFixed=json.loads(df.loc[i, 'costFixed'])
                                      , costOperation=json.loads(df.loc[i, 'costOperation'])
                                      , costSourcing=df.loc[i, 'cost_sourcing']
                                      , capacity=json.loads(df.loc[i, 'capacity'])
                                      )
            satellites[id_s] = new_satellite
        if DEBUG:
            print("-" * 50)
            print("Count of SATELLITES: ", len(satellites))
            print("First Satellite:")
            print(json.dumps(list(satellites.values())[0].__dict__, indent=2, default=str))
        return satellites, df

    @staticmethod
    def load_customer_clusters(DEBUG: bool = False) -> tuple[dict[str, Cluster], pd.DataFrame]:
        clusters = {}
        df = pd.read_csv('../others/Levantamiento de Información/Caracterización de hexagonos de La Paz.csv')

        # filtered only rows with data cajas > 0
        df = df[df['suma.cajas'] > 0].reset_index(drop=True).copy()
        #

        for i in range(len(df)):
            id_k = str(df.loc[i, 'h3_address'])

            avg_drop_by_period = list(np.float_(list(str(df.loc[i, 'avgDrop']).split("|"))))
            avg_stop_density_by_period = list(np.float_(list(str(df.loc[i, 'avgStopDensity']).split("|"))))
            demand = list(np.float_(list(str(df.loc[i, 'demand']).split("|"))))

            new_cluster = Cluster(id_c=id_k
                                  , lon=df.loc[i, 'lon.centroid']
                                  , lat=df.loc[i, 'lat.centroid']
                                  , areaKm=df.loc[i, 'area.km2']
                                  , avgTickets=df.loc[i, 'media.boletas.mes']
                                  , avgCustomers=df.loc[i, 'media.clientes.mes']
                                  , avgPackages=df.loc[i, 'media.suma.cajas.mes']
                                  , avgPackagesBySales=df.loc[i, 'media.cajas.por.venta']
                                  , packages=df.loc[i, 'suma.cajas']
                                  , sales=df.loc[i, 'Cantidad.ventas']
                                  , customers=df.loc[i, 'Total.clientes']
                                  , demand=demand
                                  , avgDrop=avg_drop_by_period
                                  , speed_intra=json.loads(df.loc[i, 'speed_intra'])
                                  , avgStopDensity=avg_stop_density_by_period
                                  , k=1
                                  )
            clusters[id_k] = new_cluster
        if DEBUG:
            print("-" * 50)
            print("Count of clusters: ", len(clusters))
            print("First segment:")
            print(json.dumps(list(clusters.values())[0].__dict__, indent=2, default=str))
        return clusters, df

    @staticmethod
    def load_distances_duration_matrix_from_satellite() -> dict[str, dict]:
        df = pd.read_csv('../others/Levantamiento de Información/Informacion Satelites a Hexagonos.csv')
        size = len(df)
        distance = dict(
            [((df.Satelite[i], df.h3_address[i]), df.loc[i, "distance.value"] / 1000) for i in range(size)]
        )
        duration = dict(
            [((df.Satelite[i], df.h3_address[i]), df.loc[i, "duration.value"] / 3600) for i in range(size)]
        )
        duration_in_traffic = dict(
            [((df.Satelite[i], df.h3_address[i]), df.loc[i, "duration_in_traffic.value"] / 3600) for i in range(size)]
        )
        matrixes = {
            'duration': duration,
            'distance': distance,
            'duration_in_traffic': duration_in_traffic
        }
        return matrixes

    @staticmethod
    def load_distances_duration_matrix_from_dc() -> dict[str, dict]:
        df = pd.read_csv('../others/Levantamiento de Información/distance_from_dc_to_clusters.csv')
        size = len(df)
        distance = dict(
            [(df.h3_address[i], df.loc[i, "distance"] / 1000) for i in range(size)]
        )
        duration = dict(
            [(df.h3_address[i], df.loc[i, "duration"] / 3600) for i in range(size)]
        )
        duration_in_traffic = dict(
            [(df.h3_address[i], df.loc[i, "duration_in_traffic"] / 3600) for i in range(size)]
        )
        matrixes = {
            'duration': duration,
            'distance': distance,
            'duration_in_traffic': duration_in_traffic
        }
        return matrixes


class Config(ABC):

    @abstractmethod
    def calculate_avg_fleet_size_from_satellites(self, satellites: list[Satellite]
                                                 , clusters: list[Cluster]
                                                 , vehicle: Vehicle
                                                 , periods: int
                                                 , distances_linehaul: dict[(str, str)]
                                                 , **params) -> dict:
        pass

    @abstractmethod
    def calculate_avg_fleet_size_from_dc(self, clusters: list[Cluster]
                                         , vehicle: Vehicle
                                         , periods: int
                                         , distances_linehaul: dict[str]
                                         , **params) -> dict[(str, int), float]:
        pass


class ConfigDeterministic(Config):

    def __init__(self) -> None:
        super().__init__()

    def avg_fleet_size(self, cluster: Cluster, vehicle: Vehicle, t: int, distance: float, **params) -> float:
        # effective vehicle capacity
        effective_vehicle_capacity = vehicle.capacity / cluster.avgDrop[t]

        # average tour time
        avg_tour_time = effective_vehicle_capacity * (
                vehicle.time_fixed +
                vehicle.time_service * cluster.avgDrop[t] +
                (vehicle.k * cluster.k) / (cluster.speed_intra[vehicle.type])
        )

        # number of fully loaded tours
        beta = vehicle.Tmax / (
                avg_tour_time +
                vehicle.time_dispatch +
                effective_vehicle_capacity * cluster.avgDrop[t] * vehicle.time_load +
                2 * (distance * vehicle.k / vehicle.speed_line)
        )

        # average fleet size
        v = (cluster.areaKm * cluster.avgStopDensity[t]) / (beta * effective_vehicle_capacity)

        return v

    # overwrite
    def calculate_avg_fleet_size_from_satellites(self, satellites: list[Satellite]
                                                 , clusters: list[Cluster]
                                                 , vehicle: Vehicle
                                                 , periods: int
                                                 , distances_linehaul: dict[(str, str)]
                                                 , **params) -> dict[(str, str, int), float]:
        fleet_size = dict([
            ((s.id, k.id, t), self.avg_fleet_size(k, vehicle, t, distances_linehaul[s.id, k.id])) for t in
            range(periods) for s in satellites for k in clusters
        ])

        return fleet_size

    def calculate_avg_fleet_size_from_dc(self, clusters: list[Cluster]
                                         , vehicle: Vehicle
                                         , periods: int
                                         , distances_linehaul: dict[str]
                                         , **params) -> dict[(str, int), float]:
        fleet_size = dict([
            ((k.id, t), self.avg_fleet_size(k, vehicle, t, distances_linehaul[k.id])) for t in range(periods) for k in
            clusters
        ])

        return fleet_size


class ConfigStochastic(Config):

    def __init__(self) -> None:
        super().__init__()

    def avg_fleet_size(self, cluster: Cluster, vehicle: Vehicle, t: int, distance: float, **params) -> float:
        pass

    def calculate_avg_fleet_size_from_satellites(self, satellites: list[Satellite]
                                                 , clusters: list[Cluster]
                                                 , vehicle: Vehicle
                                                 , periods: int
                                                 , distances_linehaul: dict[(str, str)]
                                                 , **params) -> dict[(str, str, int), float]:
        pass

    def calculate_avg_fleet_size_from_dc(self, clusters: list[Cluster]
                                         , vehicle: Vehicle
                                         , periods: int
                                         , distances_linehaul: dict[str]
                                         , **params) -> dict[(str, int), float]:
        pass
