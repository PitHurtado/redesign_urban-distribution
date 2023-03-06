from typing import Any
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
    def get_results(self, satellites: list[Satellite], clusters: list[Cluster], max_capacity) -> dict:
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
              costs: dict[str, dict], cap_max=12) -> dict[str, float]:
        self.model.reset()

        # variables
        self.__addVariables(satellites, clusters, max_capacity=cap_max)

        # objective
        self.__addObjective(satellites, clusters, costs, max_capacity=cap_max)

        # constraints
        self.__addConstr_AllocationSatellite(satellites, max_capacity=cap_max)
        self.__addConstr_OperatingSatellite(satellites, max_capacity=cap_max)
        self.__addConstr_AssignClusterToSallite(satellites, clusters, max_capacity=cap_max)
        self.__addConstr_CapacitySatellite(satellites, clusters, vehicles_required, max_capacity=cap_max)
        self.__addConstr_DemandSatified(satellites, clusters)

        # print("1) add WALDO constraints")
        # self.__addConstr_VEHICLE_dc(clusters, vehicles_required_from_dc=vehicles_required['large'], cost_dc=costs)
        # self.__addConstr_VEHICLE_satellites(satellites, clusters,
        #                                    vehicles_required_from_satellites=vehicles_required['small']
        #                                    , cost_satellites=costs)

        # print('2) W to Zero')
        # self.__addConstr_Zero_W(clusters)

        #print('3) Y to Zero')
        #self.__addConstr_Zero_Y(satellites, max_capacity=cap_max)

        #print('4) Install and operate all period - X and Y')
        #self.__addConstr_Fixed_X(satellites, max_capacity=cap_max)

        self.model.update()
        return {'time_building': 1}

    def __addVariables(self, satellites: list[Satellite], clusters: list[Cluster], max_capacity) -> None:
        self.Y = dict([
            ((s.id, q_id), self.model.addVar(vtype=GRB.BINARY, name=f'Y_s{s.id}_q{q_id}')) for s in satellites for q_id
            in s.capacity.keys() if max_capacity >= int(q_id)
        ])
        self.X = dict([
            ((s.id, q_id, t), self.model.addVar(vtype=GRB.BINARY, name=f'X_s{s.id}_t{t}')) for s in satellites for q_id
            in s.capacity.keys() for t in
            range(self.PERIODS) if max_capacity >= int(q_id)
        ])
        self.Z = dict(
            [((s.id, k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'Z_s{s.id}_k{k.id}_t{t}')) for s in satellites
             for k in clusters for t in range(self.PERIODS)]
        )
        self.W = dict([
            ((k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'W_k{k.id}_t{t}')) for k in clusters for t in
            range(self.PERIODS)
        ])

    def __addObjective(self, satellites: list[Satellite], clusters: list[Cluster], costs: dict[str, dict],
                       max_capacity):
        cost_allocation_satellites = quicksum([
            (s.costFixed[q_id] / (25 * 12)) * self.Y[(s.id, q_id)] for s in satellites for q_id in s.capacity.keys() if
            max_capacity >= int(q_id)
        ])

        cost_operating_satellites = quicksum([
            (s.costOperation[q_id][t] / 25) * self.X[(s.id, q_id, t)] for s in satellites for q_id in s.capacity.keys()
            for t in range(self.PERIODS)
            if max_capacity >= int(q_id)
        ])

        cost_served_from_satellite = quicksum([
            costs['satellite'][(s.id, k.id, t)]['total'] * self.Z[(s.id, k.id, t)] for s in satellites for k in
            clusters for t in
            range(self.PERIODS)
        ])

        cost_served_from_dc = quicksum([
            costs['dc'][(k.id, t)]['total'] * self.W[(k.id, t)] for k in clusters for t in range(self.PERIODS)
        ])

        cost_total = cost_allocation_satellites + cost_served_from_dc + cost_served_from_satellite + \
                     cost_operating_satellites
        self.model.setObjective(cost_total, GRB.MINIMIZE)

    def __addConstr_AllocationSatellite(self, satellites: list[Satellite], max_capacity):
        for s in satellites:
            nameConstraint = f'R_Open_s{s.id}'
            self.model.addConstr(
                quicksum([
                    self.Y[(s.id, q_id)] for q_id in s.capacity.keys() if max_capacity >= int(q_id)
                ]) <= 1
                , name=nameConstraint
            )

    def __addConstr_OperatingSatellite(self, satellites: list[Satellite], max_capacity):
        for t in range(self.PERIODS):
            for s in satellites:
                for q_id in s.capacity.keys():
                    if max_capacity >= int(q_id):
                        nameConstraint = f'R_Operating_s{s.id}_q{q_id}_t{t}'
                        self.model.addConstr(
                            self.X[(s.id, q_id, t)] <= self.Y[(s.id, q_id)]
                            , name=nameConstraint
                        )

    def __addConstr_AssignClusterToSallite(self, satellites: list[Satellite], clusters: list[Cluster], max_capacity):
        for t in range(self.PERIODS):
            for k in clusters:
                for s in satellites:
                    nameConstratint = f'R_Assign_s{s.id}_k{k.id}_t{t}'
                    self.model.addConstr(
                        self.Z[(s.id, k.id, t)]
                        - quicksum([
                            self.X[(s.id, q_id, t)] for q_id in s.capacity.keys() if max_capacity >= int(q_id)
                        ])
                        <= 0
                        , name=nameConstratint
                    )

    def __addConstr_CapacitySatellite(self, satellites: list[Satellite], clusters: list[Cluster]
                                      , vehicles_required: dict[str, dict], max_capacity):
        for t in range(self.PERIODS):
            for s in satellites:
                nameConstraint = f'R_capacity_s{s.id}_t{t}'
                self.model.addConstr(
                    quicksum([
                        self.Z[(s.id, k.id, t)] * vehicles_required["small"][(s.id, k.id, t)]['fleet_size']
                        for k in clusters
                    ])
                    - quicksum([
                        self.Y[(s.id, q_id)] * s.capacity[q_id] for q_id in s.capacity.keys() if
                        max_capacity >= int(q_id)
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

    def __addConstr_VEHICLE_satellites(self, satellites: list[Satellite], clusters: list[Cluster],
                                       vehicles_required_from_satellites, cost_satellites: dict[str, Any]):
        for t in range(self.PERIODS):
            for s in satellites:
                nameConstraint = f'R_waldo_s{s.id}_t{t}'
                self.model.addConstr(
                    quicksum([
                        k.demandByPeriod[t] * self.Z[(s.id, k.id, t)] for k in clusters
                    ])
                    >= quicksum([
                        cost_satellites["min_items_satellite"] * vehicles_required_from_satellites[(s.id, k.id, t)][
                            "fleet_size"] * \
                        self.Z[(s.id, k.id, t)] for k in clusters
                    ])
                    , name=nameConstraint
                )

    def __addConstr_VEHICLE_dc(self, clusters: list[Cluster], vehicles_required_from_dc, cost_dc: dict[str, Any]):
        for t in range(self.PERIODS):
            nameConstraint = f'R_waldo_t{t}'
            self.model.addConstr(
                quicksum([
                    k.demandByPeriod[t] * self.W[(k.id, t)] for k in clusters
                ])
                >=
                quicksum([
                    cost_dc["min_items_dc"] * vehicles_required_from_dc[(k.id, t)]['fleet_size'] * \
                    self.W[(k.id, t)] for k in clusters
                ])
                , name=nameConstraint
            )

    def __addConstr_Zero_W(self, clusters: list[Cluster]):
        for t in range(self.PERIODS):
            for k in clusters:
                self.model.addConstr(
                    self.W[(k.id, t)] == 0
                )

    def __addConstr_Zero_Y(self, satellites: list[Satellite], max_capacity):
        for s in satellites:
            nameConstraint = f'R_Y_zero_s{s.id}'
            self.model.addConstr(
                quicksum([
                    self.Y[(s.id, q_id)] for q_id in s.capacity.keys() if max_capacity >= int(q_id)
                ]) == 0
                , name=nameConstraint
            )

    def __addConstr_Fixed_X(self, satellites: list[Satellite], max_capacity):
        for t in range(self.PERIODS):
            for s in satellites:
                for q_id in s.capacity.keys():
                    if max_capacity >= int(q_id):
                        nameConstraint = f'R_Operating_s{s.id}_q{q_id}_t{t}'
                        self.model.addConstr(
                            self.X[(s.id, q_id, t)] == self.Y[(s.id, q_id)]
                            , name=nameConstraint
                        )

    # abstract method
    def get_results(self, satellites: list[Satellite], clusters: list[Cluster], max_capacity) -> dict:
        # variable Y
        variable_Y = dict([
            ((s.id, q_id), s) for s in satellites for q_id in s.capacity.keys() if
            (max_capacity >= int(q_id)) if (self.Y[(s.id, q_id)].x > 0)
        ])

        variable_X = dict([
            (t, dict([
                ((s.id, q_id), s) for s in satellites for q_id in s.capacity.keys() if
                (max_capacity >= int(q_id)) if  (self.X[(s.id, q_id, t)].x > 0)
            ])) for t in range(self.PERIODS)
        ])

        variable_Z = dict([
            (t, dict([
                (s.id, [
                    k for k in clusters if self.Z[(s.id, k.id, t)].x > 0
                ]) for s in satellites
            ])) for t in range(self.PERIODS)
        ])

        variable_W = dict([
            (t, [
                k for k in clusters if self.W[(k.id, t)].x > 0
            ]) for t in range(self.PERIODS)
        ])

        return {'Y': variable_Y,
                'X': variable_X,
                'Z': variable_Z,
                'W': variable_W}


class ModelStochastic(ModelMultiperiod):
    """
        SAA: Sample Average Approximation

    """

    def __init__(self, NAME_MODEL: str, first_stage_model, second_stage_model) -> None:
        super().__init__(NAME_MODEL)
        self.first_stage_model = first_stage_model
        self.second_stage_model = second_stage_model

    def build(self, first_stage_model, second_stage_model, scenarios: dict):
        pass

    def optimizeModel(self) -> str:
        # algoritmo
        pass

    # abstract method
    def get_results(self) -> dict:
        pass

# %%
