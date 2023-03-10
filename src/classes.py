class Locatable:
    def __init__(self
                 , lon: float
                 , lat: float):
        self.lon = lon
        self.lat = lat


class Cluster(Locatable):
    def __init__(self,
                 id_c: str,
                 lon: float, lat: float,
                 areaKm: float,
                 customersByPeriod: list[float],
                 demandByPeriod: list[float],
                 avgDrop: list[float],
                 speed_intra: dict[str, float],
                 avgStopDensity: list[float],
                 k: float = 0.57,
                 ):
        self.id = id_c
        Locatable.__init__(self, lon, lat)
        self.areaKm = areaKm
        self.customersByPeriod = customersByPeriod
        self.demandByPeriod = demandByPeriod
        self.avgDrop = avgDrop
        self.avgStopDensity = avgStopDensity
        self.speed_intra = speed_intra
        self.k = k


class Satellite(Locatable):
    def __init__(self,
                 id_s: str,
                 lon: float, lat: float,
                 distanceFromDC: float,
                 durationFromDC: float,
                 durationInTrafficFromDC: float,
                 costFixed: dict[str, float],
                 costOperation: list[float],
                 costSourcing: float,
                 capacity: dict[str, float]
                 ):
        self.id = id_s
        Locatable.__init__(self, lon, lat)

        self.distanceFromDC = distanceFromDC
        self.durationFromDC = durationFromDC
        self.durationInTrafficFromDC = durationInTrafficFromDC
        self.costFixed = costFixed
        self.costOperation = costOperation
        self.costSourcing = 0.389
        self.capacity = capacity


class Vehicle:
    def __init__(self
                 , id: str
                 , type: str
                 , capacity: float
                 , costFixed: float
                 , time_service: float
                 , time_fixed: float
                 , time_dispatch: float
                 , time_load: float
                 , speed_line: float
                 , Tmax: float
                 , k: float):
        self.id = str(id)
        self.type = type
        self.capacity = capacity
        self.costFixed = costFixed
        self.time_fixed = time_fixed
        self.time_service = time_service
        self.time_dispatch = time_dispatch
        self.time_load = time_load
        self.speed_line = speed_line
        self.Tmax = Tmax
        self.k = k
