import gurobipy as gb
from gurobipy import GRB, quicksum
from classes import Cluster, Satellite


class Model_Multiperiod:
    def __init__(self, periods: int, name_model="Deterministic"):
        self.model = gb.Model(name_model)
        self.PERIODS = periods

        # variables
        self.X = {}
        self.Y = {}
        self.W = {}

        # objetive & metrics
        self.results = {}
        self.metrics = {}

    def build(self, satellites: list[Satellite], segments: list[Cluster], vehicles_required: dict[str, dict],
              costs: dict[str, dict]):
        self.model.reset()

        # variables
        self.__addVariables(satellites, segments)

        # objective
        self.__addObjective(satellites, segments, costs)

        # constraints
        self.__addConstr_AllocationSatellite(satellites)
        self.__addConstr_CapacitySatellite(satellites, segments, vehicles_required)
        self.__addConstr_DemandSatified(satellites, segments)

    def __addVariables(self, satellites: list[Satellite], segments: list[Cluster]):
        self.Y = dict([
            ((s.id, q_id), self.model.addVar(vtype=GRB.BINARY, name=f'Y_s{s.id}_q{q_id}')) for s in satellites for q_id
            in s.capacity.keys()
        ])
        self.X = dict(
            [((s.id, k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'X_s{s.id}_k{k.id}_t{t}')) for s in satellites
             for k in segments for t in range(self.PERIODS)]
        )
        self.W = dict([
            ((k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'W_k{k.id}_t{t}')) for k in segments for t in
            range(self.PERIODS)
        ])

    def __addObjective(self, satellites: list[Satellite], segments: list[Cluster], costs: dict[str, dict]):
        cost_allocation_satellites = quicksum([
            s.costFixed[q_id] * self.Y[(s.id, q_id)] for s in satellites for q_id in s.capacity.keys()
        ])

        cost_served_from_satellite = quicksum([
            costs['satellite'][(s.id, k.id, t)] * self.X[(s.id, k.id, t)] for s in satellites for k in segments for t in
            range(self.PERIODS)
        ])

        cost_served_from_dc = quicksum([
            costs['dc'][(k.id, t)] * self.W[(k.id, t)] for k in segments for t in range(self.PERIODS)
        ])

        cost_total = cost_allocation_satellites + cost_served_from_dc + cost_served_from_satellite
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

    def __addConstr_CapacitySatellite(self, satellites: list[Satellite], segments: list[Cluster],
                                      vehicles_required: dict[str, dict]):
        for t in range(self.PERIODS):
            for s in satellites:
                nameConstraint = f'R_capacity_s{s.id}_t{t}'
                self.model.addConstr(
                    quicksum([
                        self.X[(s.id, k.id, t)] * vehicles_required["small"][(s.id, k.id, t)] for k in segments
                    ])
                    - quicksum([
                        self.Y[(s.id, q_id)] * s.capacity[q_id] for q_id in s.capacity.keys()
                    ])
                    <= 0
                    , name=nameConstraint
                )

    def __addConstr_DemandSatified(self, satellites: list[Satellite], segments: list[Cluster]):
        for t in range(self.PERIODS):
            for k in segments:
                nameConstraint = f'R_demand_k{k.id}_t{t}'
                self.model.addConstr(
                    quicksum([
                        self.X[(s.id, k.id, t)] for s in satellites
                    ])
                    + quicksum([
                        self.W[(k.id, t)]
                    ])
                    == 1
                    , name=nameConstraint
                )

    def optimizeModel(self) -> str:
        self.model.optimize()
        return self.model.Status

    def showModel(self):
        self.model.display()

    def setParams(self, params: dict[str, int]):
        for key, item in params.items():
            self.model.setParam(key, item)
