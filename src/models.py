import gurobipy as gb
from gurobipy import GRB, quicksum
from classes import Customer, Satellite, Vehicle

class Model_Multiperiod:

    def __init__(self, periods: int, name_model="Deterministic"):
        self.model = gb.Model(name_model)
        self.PERIODS = periods

        # variables
        self.X = {}
        self.Y = {}
        self.W = {}
        self.Z = {}
        self.R = {}
        self.ALPHA = {}
        self.BETA = {}

        # objetive & metrics
        self.results = {}
        self.metrics = {}

    def build(self, customers: list[Customer], satellites: list[Satellite], **params):
        self.model.reset()
        # variables
        self.__addVariables(customers, satellites)
        # objective
        self.__addObjective(customers, satellites, large_vehicle=params['large_vehicle'], small_vehicle=params['small_vehicle'])
        # constraints
        self.__addConstr_LocationSatellite(satellites)
        self.__addConstr_AssignSatellite(satellites, customers)
        self.__addConstr_NumberVehiclesSatellite(satellites, customers, small_vehicle=params['small_vehicle'])
        self.__addConstr_NumberVehiclesDC(customers, large_vehicle=params['large_vehicle'])
        self.__addConstr_DemandSatified_lowCustomers(customers, satellites)
        self.__addConstr_DemandSatified_highCustomers(customers)
        self.__addConstr_Alpha(customers, satellites)
        self.__addConstr_Beta(customers)
        self.__addConstr_vehicles_installed(customers)

    def __addVariables(self, customers: list[Customer], satellites: list[Satellite]):
        self.Y = dict(
            [(s.id, self.model.addVar(vtype=GRB.BINARY, name=f'Y_s{s.id}')) for s in satellites]
        )
        self.X = dict(
            [((s.id, k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'X_s{s.id}_k{k.id}_t{t}')) for s in satellites for k in customers for t in range(self.PERIODS)]
        )
        self.W = dict(
            [((k.id, t), self.model.addVar(vtype=GRB.BINARY, name=f'W_k{k.id}_t{t}')) for k in customers for t in range(self.PERIODS)]
        )
        self.Z = dict(
            [((s.id, t), self.model.addVar(vtype=GRB.INTEGER, lb=0.0, name=f'Z_s{s.id}_t{t}')) for s in satellites for t in range(self.PERIODS)]
        )
        self.R = dict(
            [(t, self.model.addVar(vtype=GRB.INTEGER, lb=0.0, name=f"R_t{t}")) for t in range(self.PERIODS)]
        )
        self.ALPHA = dict(
            [((s.id, k.id), self.model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name=f"ta_s{s.id}_k{k.id}")) for s in satellites for k in customers]
        )
        self.BETA = dict(
            [(k.id, self.model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name=f'tb_k{k.id}')) for k in customers]
        )
        self.Q = dict([
            (s.id, self.model.addVar(vtype=GRB.INTEGER, lb=0.0, name=f'Q_s{s.id}')) for s in satellites
        ])

    def __addObjective(self, customers: list[Customer], satellites: list[Satellite], large_vehicle: Vehicle, small_vehicle: Vehicle):
        cost_num_large_vehicle = quicksum(
            [large_vehicle.cost * self.R[t] for t in range(self.PERIODS)]
        )

        cost_served_from_dc = quicksum(
            [self.BETA[k.id] * self.W[(k.id, t)] for t in range(self.PERIODS) for k in customers]
        )
        
        cost_allocation_satellites = quicksum(
            [s.costFixed * self.Y[s.id] for s in satellites]
        )

        cost_num_small_vehicle = quicksum(
            [small_vehicle.cost * self.Z[(s.id, t)] for s in satellites for t in range(self.PERIODS)]
        )

        cost_served_from_satellite = quicksum(
            [self.ALPHA[(s.id, k.id) * self.X[(s.id, k.id, t)]] for s in satellites for k in customers for t in range(self.PERIODS)]
        )

        cost_total = cost_num_large_vehicle + cost_num_small_vehicle + cost_allocation_satellites + cost_served_from_dc + cost_served_from_satellite
        self.model.setObjective(cost_total, GRB.MINIMIZE)

    def __addConstr_LocationSatellite(self, satellites: list[Satellite]):
        for s in satellites:
            nameConstraint = f'R_Open_s{s.id}'
            self.model.addConstr(
                quicksum([self.Y[s.id]]) <= 1
                , name=nameConstraint
            )

    def __addConstr_AssignSatellite(self, satellite: list[Satellite], customers: list[Customer]):
        for s in satellite:
            for k in customers:
                if k.isLow:
                    for t in range(self.PERIODS):
                        nameConstraint = f'R_assign_s{s.id}_k{k.id}_t{t}'
                        self.model.addConstr(
                            self.X[(s.id, k.id, t)] <= self.Y[s.id]
                            , name=nameConstraint
                        )

    def __addConstr_NumberVehiclesSatellite(self, customers: list[Customer], satellites: list[Satellite], small_vehicle: Vehicle):
        for s in satellites:
            for t in range(self.PERIODS):
                nameConstraint = f'R_numVeh_s{s.id}_t{t}'
                self.model.addConstr(
                    quicksum(
                        [k.demand[t] * self.X[(s.id, k.id, t)] for k in customers if k.isLow]
                    )
                    - quicksum(
                        [small_vehicle.capacity * self.Z[(s.id,t)]]
                    )
                    <= 0
                    , name=nameConstraint
                )

    def __addConstr_NumberVehiclesDC(self, customers: list[Customer], large_vehicle: Vehicle):
        for t in range(self.PERIODS):
            nameConstraint = f"R_numVeh_DC_t{t}"
            self.model.addConstr(
                quicksum(
                    [k.demand[t] * self.W[(k.id, t)] for k in customers]
                )
                - quicksum(
                    [large_vehicle.capacity * self.R[t]]
                )
                <= 0
                , name=nameConstraint
            )

    def __addConstr_DemandSatified_lowCustomers(self, customers: list[Customer], satellites: list[Satellite]):
        for k in customers:
            if k.isLow:
                for t in range(self.PERIODS):
                    nameConstraint = f'R_Demand_low_k{k.id}_t{t}'
                    self.model.addConstr(
                        quicksum(
                            [self.X[(s.id, k.id, t)] for s in satellites].append(self.W[(k.id, t)])
                        )
                        == 1
                        , name=nameConstraint
                    )

    def __addConstr_DemandSatified_highCustomers(self, customers: list[Customer]):
        for t in range(self.PERIODS):
            for k in customers:
                if k.isLow:
                    continue
                nameConstraint = f'R_Demand_high_k{k.id}_t{t}'
                self.model.addConstr(
                    quicksum(
                        [self.W[(k.id, t)]]
                    )
                    == 1
                    , name=nameConstraint
                )

    def __addConstr_Alpha(self, customers: list[Customer], satellites: list[Satellite]):
        for s in satellites:
            for k in customers:
                if k.isLow:
                    nameConstraint = f'R_alpha_s{s.id}_k{k.id}'
                    self.model.addConstr(
                        self.ALPHA[(s.id, k.id)]
                        >= k.fee_min_satellite
                        , name=nameConstraint
                    )

    def __addConstr_Beta(self, customers: list[Customer]):
        for k in customers:
            if k.isLow:
                continue
            nameConstraint = f'R_beta_k{k.id}'
            self.model.addConstr(
                self.BETA[k.id]
                >= k.fee_min_dc
                , name=nameConstraint
            )

    def __addConstr_vehicles_installed(self, satellites: list[Satellite]):
        for t in range(self.PERIODS):
            for s in satellites:
                nameConstraint = f'R_installed_vehicles_s{s.id}_t{t}'
                self.model.addConstr(
                    self.Z[(s.id, t)] - self.Q[s.id]
                    <= 0
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
