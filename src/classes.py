class Segment:
    def __init__(self,
                id: str,
                lon: float, lat: float,
                areaKm: float,
                avgTickets: float,
                avgCustomers: float,
                avgPackages: float,
                avgPackagesBySales: float,
                packages: float,
                sales: float,
                customers: int,
                avgDropSize: float,
                setSatellitesCoverage: list[str],
                costServedFromDC: int,
                ):
        self.id = id
        self.geographyLocation = (lon, lat)
        self.areaKm = areaKm
        self.avgTickets = avgTickets
        self.avgCustomers = avgCustomers
        self.avgPackages = avgPackages
        self.avgPackagesBySales = avgPackagesBySales
        self.packages = packages
        self.customers = customers
        self.sales = sales
        self.avgDropSize = avgDropSize
        self.setSatelliteCoverage = setSatellitesCoverage
        self.costServedFromDC = costServedFromDC


class Satellite:
    def __init__(self,
                id: str,
                lon: float, lat: float,
                distanceFromDC: float,
                durationFromDC: float,
                durationInTrafficFromDC: float,
                costFixed: dict[str, float],
                costPerVehicle: float,
                capacity: dict[str, float]
                ):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.geographyLocation = (lon, lat)
        self.distanceFromDC = distanceFromDC
        self.durationFromDC = durationFromDC
        self.durationInTrafficFromDC = durationInTrafficFromDC
        self.costFixed = costFixed
        self.capacity = capacity


# class Customer:
#     def __init__(self,
#                 id: str,
#                 lon: float, lat: float,
#                 demand: list[float],
#                 category: float,
#                 isLow: bool,
#                 fee_min_satellite: float,
#                 fee_min_dc: float,
#                 ):
#         self.id = str(id)
#         self.lon = lon
#         self.lat = lat
#         self.geographyLocation = (lon, lat)
#         self.demand = demand
#         self.category = category
#         self.isLow = isLow
#         self.fee_min_satellite = fee_min_satellite
#         self.fee_min_dc = fee_min_dc


class Vehicle:
    def __init__(self
                , id: str
                , capacity: float
                , costFixed: float):
        self.id = str(id)
        self.capacity = capacity
        self.costFixed = costFixed
