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
                costFixed: float,
                costPerVehicle: float,
                ):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.geographyLocation = (lon, lat)
        self.distanceFromDC = distanceFromDC
        self.durationFromDC = durationFromDC
        self.durationInTrafficFromDC = durationInTrafficFromDC
        self.costFixed = costFixed
        self.costPerVehicle = costPerVehicle


class Customer:
    def __init__(self,
                id: str,
                lon: float, lat: float,
                demand: float,
                category: float,
                isLow: bool,
                fee_min_satellite: float,
                fee_min_dc:float
                ):
        self.id = str(id)
        self.lon = lon
        self.lat = lat
        self.geographyLocation = (lon, lat)
        self.demand = demand
        self.category = category
        self.isLow = isLow
        self.fee_min_satellite = fee_min_satellite
        self.fee_min_dc = fee_min_dc


class Vehicle:
    def __init(self,
                id: str,
                capacity: float):
        self.id = str(id)
        self.capacity = capacity
