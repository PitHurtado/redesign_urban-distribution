class Segment:
    # All parameters are by Month
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
                 setSatelitesCoverage: list[str],
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
        self.setSateliteCoverage = setSatelitesCoverage
        self.costServedFromDC = costServedFromDC


class Satelite:
    def __init__(self,
                 id: str,
                 lon: float, lat: float,
                 distanceFromDC: float,
                 durationFromDC: float,
                 durationInTrafficFromDC: float,
                 capacity: dict[str, int],
                 numberVehiclesAvailable: dict[str, int],
                 costFixed: dict[str, int],
                 setSegmentCoverage: list[str],
                 ):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.geographyLocation = (lon, lat)
        self.distanceFromDC = distanceFromDC
        self.durationFromDC = durationFromDC
        self.durationInTrafficFromDC = durationInTrafficFromDC
        self.capacity = capacity
        self.numberVehiclesAvailable = numberVehiclesAvailable
        self.costFixed = costFixed
        self.setSegmentCoverage = setSegmentCoverage


class Customer:
    def __init__(self,
                 id: str,
                 lon: float, lat: float,
                 demand: float,
                 category: float
                 ):
        self.id = str(id)
        self.lon = lon
        self.lat = lat
        self.geographyLocation = (lon, lat)
        self.demand = demand
        self.category = category
