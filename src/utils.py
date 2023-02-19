import json
import math

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from classes import Satellite, Cluster, Vehicle


class LoadingData:
    @staticmethod
    def load_satellites(DEBUG: bool = False) -> tuple[dict[str, Satellite], pd.DataFrame]:
        satellites = {}
        df = pd.read_csv('../others/data/base_satellites_READY_zoom_7.csv')
        for i in range(len(df)):
            id_s = str(df.id_satellite[i])
            cost_operation = list(np.float_(list(str(df.loc[i, 'costOperation']).split("|"))))
            cost_sourcing = df.loc[i, 'costSourcing']
            capacity = json.loads(df.loc[i, 'capacity'])
            new_satellite = Satellite(id_s=id_s
                                      , lon=df.lon[i]
                                      , lat=df.lat[i]
                                      , distanceFromDC=df.loc[i, 'distance'] / 1000
                                      , durationFromDC=df.loc[i, 'duration'] / 3600
                                      , durationInTrafficFromDC=df.loc[i, 'duration_in_traffic'] / 3600
                                      , costFixed=json.loads(df.loc[i, 'costFixed'])
                                      , costOperation=cost_operation
                                      , costSourcing=cost_sourcing
                                      , capacity=capacity
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
        df = pd.read_csv('../others/data/base_cluster_READY_zoom_7.csv')

        # filtered only rows with data cajas > 0
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        #

        for i in range(len(df)):
            id_k = str(df.loc[i, 'id_cluster'])

            avg_drop_by_period = list(np.float_(list(str(df.loc[i, 'avgDrop']).split("|"))))
            avg_stop_density_by_period = list((np.float_(list(str(df.loc[i, 'avgStop']).split("|")))))
            demand_by_period = list((np.float_(list(str(df.loc[i, 'demandByPeriod']).split("|")))))
            customers_by_period = list((np.float_(list(str(df.loc[i, 'avg_customers']).split("|")))))
            new_cluster = Cluster(id_c=id_k
                                  , lon=df.loc[i, 'lon']
                                  , lat=df.loc[i, 'lat']
                                  , areaKm=df.loc[i, 'area_km']
                                  , customersByPeriod=customers_by_period
                                  , demandByPeriod=demand_by_period
                                  , avgDrop=avg_drop_by_period
                                  , speed_intra=json.loads(df.loc[i, 'intra_stop_speed'])
                                  , avgStop=avg_stop_density_by_period
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
        df = pd.read_csv('../others/data/matrix_distance_satellite_to_cluster_READY.csv')
        size = len(df)
        distance = dict(
            [((df.id_satellite[i], df.id_cluster[i]), df.loc[i, "distance"] / 1000) for i in range(size)]
        )
        duration = dict(
            [((df.id_satellite[i], df.id_cluster[i]), df.loc[i, "duration"] / 3600) for i in range(size)]
        )
        duration_in_traffic = dict(
            [((df.id_satellite[i], df.id_cluster[i]), df.loc[i, "duration_in_traffic"] / 3600) for i in range(size)]
        )
        matrixes = {
            'duration': duration,
            'distance': distance,
            'duration_in_traffic': duration_in_traffic
        }
        return matrixes

    @staticmethod
    def load_distances_duration_matrix_from_dc() -> dict[str, dict]:
        df = pd.read_csv('../others/data/matrix_distance_dc_to_clusters_READY.csv')
        size = len(df)
        distance = dict(
            [(df.id_cluster[i], df.loc[i, "distance"] / 1000) for i in range(size)]
        )
        duration = dict(
            [(df.id_cluster[i], df.loc[i, "duration"] / 3600) for i in range(size)]
        )
        duration_in_traffic = dict(
            [(df.id_cluster[i], df.loc[i, "duration_in_traffic"] / 3600) for i in range(size)]
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

    def avg_fleet_size(self, cluster: Cluster, vehicle: Vehicle, t: int, distance: float, **params) -> dict[str, float]:
        # effective vehicle capacity
        if cluster.avgDrop[t] <= 0:
            return {'fleet_size': 0, 'avg_tour_time': 0, 'fully_loaded_tours': 0,
                    'effective_capacity': 0, "demand_served": cluster.demandByPeriod[t],
                    'avg_drop': cluster.avgDrop[t], 'avg_stop_density': cluster.avgStop[t]}

        effective_vehicle_capacity = (vehicle.capacity / cluster.avgDrop[t])

        # time services
        time_services = vehicle.time_fixed + vehicle.time_service * cluster.avgDrop[t]

        # time intra stop
        time_intra_stop = (vehicle.k * cluster.k) / (cluster.speed_intra[vehicle.type]*math.sqrt(cluster.avgDrop[t]/cluster.areaKm))

        # average tour time
        avg_tour_time = effective_vehicle_capacity * (
                time_services +
                time_intra_stop
        )

        # time preparing
        time_preparing_dispatch = vehicle.time_dispatch + effective_vehicle_capacity * cluster.avgDrop[t] * vehicle.time_load

        # time line_haul
        time_line_haul = 2 * (distance * vehicle.k / vehicle.speed_line)

        # number of fully loaded tours
        beta = vehicle.Tmax / (
                avg_tour_time +
                time_preparing_dispatch +
                time_line_haul
        )

        # average fleet size
        numerador = (cluster.avgStop[t])
        denominador = beta * effective_vehicle_capacity
        v = (numerador / denominador) if denominador > 0 else 0.0

        return {'fleet_size': v, 'avg_tour_time': avg_tour_time, 'fully_loaded_tours': beta,
                'effective_capacity': effective_vehicle_capacity, "demand_served": cluster.demandByPeriod[t],
                'avg_drop': cluster.avgDrop[t], 'avg_stop_density': cluster.avgStop[t]}

    # overwrite
    def calculate_avg_fleet_size_from_satellites(self, satellites: list[Satellite]
                                                 , clusters: list[Cluster]
                                                 , vehicle: Vehicle
                                                 , periods: int
                                                 , distances_linehaul: dict[(str, str)]
                                                 , **params) -> dict[(str, str, int), dict]:
        fleet_size = dict([
            ((s.id, k.id, t), self.avg_fleet_size(k, vehicle, t, distances_linehaul[(s.id, k.id)])) for t in
            range(periods) for s in satellites for k in clusters
        ])

        return fleet_size

    def calculate_avg_fleet_size_from_dc(self, clusters: list[Cluster]
                                         , vehicle: Vehicle
                                         , periods: int
                                         , distances_linehaul: dict[str]
                                         , **params) -> dict[(str, int), dict]:
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
