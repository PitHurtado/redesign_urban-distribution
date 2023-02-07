import gurobipy as gb
from gurobipy import GRB, quicksum
from src.classes import Cluster, Satellite
from abc import ABC, abstractmethod


class ModelMultiperiod(ABC):

    def __init__(self, NAME_MODEL: str) -> None:
        self.model = gb.Model(NAME_MODEL)

    def optimizeModel(self) -> str:
        self.model.optimize()
        return self.model.Status

    def showModel(self):
        self.model.display()

    def setParams(self, params: dict[str, int]):
        for key, item in params.items():
            self.model.setParam(key, item)

    @abstractmethod
    def get_results(self, satellites: list[Satellite], clusters: list[Cluster]) -> dict:
        pass


class ModelDeterministic(ModelMultiperiod):
    """
    DocString

    """

    def __init__(self, periods: int, name_model="Deterministic-MultiPeriod"):
        super().__init__(NAME_MODEL=name_model)

        self.PERIODS = periods

        # variables
        self.X = {}
        self.Y = {}
        self.W = {}
        self.Z = {}

        # objetive & metrics
        self.results = {}
        self.metrics = {}

    def build(self, satellites: list[Satellite], clusters: list[Cluster], vehicles_required: dict[str, dict],
              costs: dict[str, dict]) -> dict[str, float]:
        self.model.reset()

        # variables
        self.__addVariables(satellites, clusters)

        # objective
        self.__addObjective(satellites, clusters, costs)

        # constraints
        self.__addConstr_AllocationSatellite(satellites)
        self.__addConstr_OperatingSatellite(satellites)
        self.__addConstr_AssignClusterToSallite(satellites, clusters)
        self.__addConstr_CapacitySatellite(satellites, clusters, vehicles_required)
        self.__addConstr_DemandSatified(satellites, clusters)

        return {'time_building': 1000}

    def __addVariables(self, satellites: list[Satellite], clusters: list[Cluster]) -> None:
        self.Y = dict([
            ((s.id, q_id), self.model.addVar(vtype=GRB.BINARY, name=f'Y_s{s.id}_q{q_id}')) for s in satellites for q_id
            in s.capacity.keys()
        ])
        self.X = dict([
            ((s.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'X_s{s.id}_t{t}')) for s in satellites for t in
            range(self.PERIODS)
        ])
        self.Z = dict(
            [((s.id, k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'Z_s{s.id}_k{k.id}_t{t}')) for s in satellites
             for k in clusters for t in range(self.PERIODS)]
        )
        self.W = dict([
            ((k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'W_k{k.id}_t{t}')) for k in clusters for t in
            range(self.PERIODS)
        ])

    def __addObjective(self, satellites: list[Satellite], clusters: list[Cluster], costs: dict[str, dict]):
        cost_allocation_satellites = quicksum([
            s.costFixed[q_id] * self.Y[(s.id, q_id)] for s in satellites for q_id in s.capacity.keys()
        ])

        cost_operating_satellites = quicksum([
            s.costOperation[t] * self.X[(s.id, t)] for s in satellites for t in range(self.PERIODS)
        ])

        cost_served_from_satellite = quicksum([
            costs['satellite']['total_cost'][(s.id, k.id, t)] * self.X[(s.id, k.id, t)] for s in satellites for k in
            clusters for t in
            range(self.PERIODS)
        ])

        cost_served_from_dc = quicksum([
            costs['dc']['total_cost'][(k.id, t)] * self.W[(k.id, t)] for k in clusters for t in range(self.PERIODS)
        ])

        cost_total = cost_allocation_satellites + cost_served_from_dc + cost_served_from_satellite + cost_operating_satellites
        self.model.setObjective(cost_total, GRB.MINIMIZE)

    def __addConstr_AllocationSatellite(self, satellites: list[Satellite]):
        for s in satellites:
            nameConstraint = f'R_Open_s{s.id}'
            self.model.addConstr(
                quicksum([
                    self.Y[(s.id, q_id)] for q_id in s.capacity.keys()
                ]) <= 1
                , name=nameConstraint
            )

    def __addConstr_OperatingSatellite(self, satellites: list[Satellite]):
        for t in range(self.PERIODS):
            for s in satellites:
                nameConstraint = f'R_Operating_s{s.id}_{t}'
                self.model.addConstr(
                    self.X[(s.id, t)]
                    - quicksum([
                        self.Y[(s.id, q_id, t)] for q_id in s.capacity.keys()
                    ])
                    <= 0
                    , name=nameConstraint
                )

    def __addConstr_AssignClusterToSallite(self, satellites: list[Satellite], clusters: list[Cluster]):
        for t in range(self.PERIODS):
            for k in clusters:
                for s in satellites:
                    nameConstratint = f'R_Assign_s{s.id}_k{k.id}_t{t}'
                    self.model.addConstr(
                        self.Z[(s.id, k.id, t)] - self.X[(s.id, t)]
                        <= 0
                        , name=nameConstratint
                    )

    def __addConstr_CapacitySatellite(self, satellites: list[Satellite], clusters: list[Cluster]
                                      , vehicles_required: dict[str, dict]):
        for t in range(self.PERIODS):
            for s in satellites:
                nameConstraint = f'R_capacity_s{s.id}_t{t}'
                self.model.addConstr(
                    quicksum([
                        self.Z[(s.id, k.id, t)] * vehicles_required["small"][(s.id, k.id, t)] for k in clusters
                    ])
                    - quicksum([
                        self.Y[(s.id, q_id)] * s.capacity[q_id] for q_id in s.capacity.keys()
                    ])
                    <= 0
                    , name=nameConstraint
                )

    def __addConstr_DemandSatified(self, satellites: list[Satellite], clusters: list[Cluster]):
        for t in range(self.PERIODS):
            for k in clusters:
                nameConstraint = f'R_demand_k{k.id}_t{t}'
                self.model.addConstr(
                    quicksum([
                        self.Z[(s.id, k.id, t)] for s in satellites
                    ])
                    + quicksum([
                        self.W[(k.id, t)]
                    ])
                    == 1
                    , name=nameConstraint
                )

    # abstract method
    def get_results(self, satellites: list[Satellite], clusters: list[Cluster]) -> dict:
        pass


class ModelStochastic(ModelMultiperiod):
    """
    DocString

    """

    def __init__(self, NAME_MODEL: str) -> None:
        super().__init__(NAME_MODEL)

    # abstract method
    def get_results(self) -> dict:
        pass
