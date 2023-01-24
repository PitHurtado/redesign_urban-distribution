class Locatable:
    def __init__(self
               , lon: float
               , lat: float):
        self.lon = lon
        self.lat = lat

class Segment(Locatable):
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
                k: float = 0,
                ):
        self.id = id
        Locatable.__init__(self,lon, lat)
        self.areaKm = areaKm
        self.avgTickets = avgTickets
        self.avgCustomers = avgCustomers
        self.avgPackages = avgPackages
        self.avgPackagesBySales = avgPackagesBySales
        self.packages = packages
        self.customers = customers
        self.sales = sales
        self.avgDropSize = avgDropSize
        self.k = k



class Satellite(Locatable):
    def __init__(self,
                id: str,
                lon: float, lat: float,
                distanceFromDC: float,
                durationFromDC: float,
                durationInTrafficFromDC: float,
                costFixed: dict[str, float],
                capacity: dict[str, float]
                ):
        self.id = id
        Locatable.__init__(self, lon, lat)

        self.distanceFromDC = distanceFromDC
        self.durationFromDC = durationFromDC
        self.durationInTrafficFromDC = durationInTrafficFromDC
        self.costFixed = costFixed
        self.capacity = capacity


class Vehicle:
    def __init__(self
                , id: str
                , capacity: float
                , costFixed: float):
        self.id = str(id)
        self.capacity = capacity
        self.costFixed = costFixed
