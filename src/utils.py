from classes import Satellite, Cluster, Vehicle

def avg_fleet_size(cluster: Cluster, vehicle: Vehicle, t: int, distance: float) -> float:
  """
  Parameter: Average Fleet Size
  
  Description
  -----------
  this method compute parameter v_{skv}^{t}, which is the number of vehicles type v needed to serve customer cluster k in period t.

  """

  # effective vehicle capacity
  effective_vehicle_capacity = vehicle.capacity / cluster.avgDropSize[t]

  # average tour time
  avg_tour_time = effective_vehicle_capacity*(
      vehicle.time_fixed + \
      vehicle.time_service * cluster.avgDrop[t] + \
      (vehicle.k*cluster.k)/(cluster.speed_intra[vehicle.type])
  )
  
  # number of fully loaded tours 
  beta = vehicle.Tmax / (
    avg_tour_time + \
    vehicle.time_dispatch + \
    effective_vehicle_capacity * cluster.avgDrop[t] * vehicle.time_load + \
    2*(distance*vehicle.k / vehicle.speed_line)
  )

  # average fleet size
  v = (cluster.areaKm * cluster.avgStopDensity[t])/(beta * effective_vehicle_capacity)

  return v


def calculate_avg_fleet_size(satellites: list[Satellite]
                            , clusters: list[Cluster]
                            , vehicle: Vehicle
                            , periods: int
                            , distances_linehaul: dict[(str, str)]) -> dict[(str, str, int), float]:
  """
  Description
  -----------
  avg fleet size calculated from satellites to customer clusters

  """

  fleet_size = dict([
    ((s.id, k.id, t), avg_fleet_size(k, vehicle, t, distances_linehaul[s.id, k.id])) for t in range(periods) for s in satellites for k in clusters
  ])

  return fleet_size

def calculate_avg_fleet_size(clusters: list[Cluster]
                            , vehicle: Vehicle
                            , periods: int
                            , distances_linehaul: dict[str]) -> dict[(str, int), float]:
  """
  Description
  -----------
  avg fleet size calculated from DC to customer clusters

  """
  fleet_size = dict([
    ((k.id, t), avg_fleet_size(k, vehicle, t, distances_linehaul[k.id])) for t in range(periods) for k in clusters
  ])

  return fleet_size
