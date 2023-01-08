#import gurobipy as gp
#from gurobipy import GRB, quicksum
from classes import Customer, Satellite

class Model:

    def __init__(self, name_model="Deterministic"):
        self.model = gb.Model(name_model)

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
        self.__addObjective(customers, satellites, params)
        # constraints
        self.__addConstr_LocationSatellite(satellites)
        self.__addConstr_AssignSatellite(satellites, customers)
        self.__addConstr_NumberVehiclesSatellite(satellites, customers, params)
        self.__addConstr_NumberVehiclesDC(customers, params)
        self.__addConstr_DemandSatified_large(customers)
        self.__addConstr_Alpha(customers, satellites)
        self.__addConstr_Beta(customers)

    def __addVariables(self, customers: list[Customer], satellites: list[Satellite]):
        self.Y = dict(
            [(s.id, self.model.addVar(vtype=GRB.BINARY, name="Y_s%s" % s.id)) for s in satellites]
        )
        self.X = dict(
            [((s.id, k.id), self.model.addVar(vtype=GRB.BINARY, name="X_s%s_k%s" % (s.id, k.id))) for s in satellites
             for k in customers]
        )
        self.W = dict(
            [(k.id, self.model.addVar(vtype=GRB.BINARY, name="W_k%s" % k.id)) for k in customers]
        )
        self.Z = dict(
            [(s.id, self.model.addVar(vtype=GRB.INTEGER, lb=0.0, name="Z_s%s" % s.id)) for s in satellites]
        )
        self.R = self.model.addVar(vtype=GRB.INTEGER, lb=0.0, name="R_")
        self.ALPHA = dict(
            [((s.id, k.id), self.model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="A_s%s_k%s" % (s.id, k.id))) for s in
             satellites for k in customers]
        )
        self.BETA = dict(
            [(k.id, self.model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="B_k%s" % k.id)) for k in customers]
        )

    def __addObjective(self, customers: list[Customer], satellites: list[Satellite], params):
        cost_location = quicksum(
            [s.costFixed * self.Y[s.id] for s in satellites]
        )
        cost_number_vehicles_satellites = quicksum(
            [s.costPerVehicle * self.Z[s.id] for s in satellites]
        )
        cost_number_vehicles_dc = quicksum(
            [params['cost_per_vehicle'] * self.R]
        )
        cost_items_satellite = quicksum(
            [params['tariff_from_satellite'][(s.id, k.id)] * self.ALPHA[(s.id, k.id)] for s in satellites for k in
             customers if k.isSmall]
        )
        cost_items_dc = quicksum(
            [params['tariff_from_dc'][k.id] * self.BETA[k.id] for k in customers]
        )
        cost_total = cost_location + cost_number_vehicles_satellites + cost_number_vehicles_dc + cost_items_satellite + cost_items_dc
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
                if k.isSmall:
                    nameConstraint = f'R_assign_s{s.id}_k{k.id}'
                    self.model.addConstr(
                        self.X[(s.id, k.id)] <= self.Y[s.id]
                        , name=nameConstraint
                    )

    def __addConstr_NumberVehiclesSatellite(self, customers: list[Customer], satellites: list[Satellite], params):
        for s in satellites:
            nameConstraint = f'R_numV_s{s.id}'
            self.model.addConstr(
                quicksum(
                    [k.demand * self.X[(s.id, k.id)] for k in customers if k.isSmall]
                )
                - quicksum(
                    [params['capacity_small_vehicle'] * self.Z[s.id]]
                )
                <= 0
                , name=nameConstraint
            )

    def __addConstr_NumberVehiclesDC(self, customers: list[Customer], params):
        nameConstraint = "R_numV_DC"
        self.model.addConstr(
            quicksum(
                [k.demand * self.W[k.id] for k in customers]
            )
            - quicksum(
                [params['capacity_large_vehicle'] * self.R]
            )
            <= 0
            , name=nameConstraint
        )

    def __addConstr_DemandSatified_small(self, customers: list[Customer], satellites: list[Satellite]):
        for k in customers:
            if k.isSmall:
                nameConstraint = f'R_Demand_k{k.id}'
                self.model.addConstr(
                    quicksum(
                        [self.X[(s.id, k.id)] for s in satellites].append(self.W[k.id])
                    )
                    == 1
                    , name=nameConstraint
                )
    def __addConstr_DemandSatified_large(self, customers: list[Customer]):
        for k in customers:
            if k.isSmall:
                continue
            nameConstraint = f'R_Demand_k{k.id}'
            self.model.addConstr(
                quicksum(
                    [self.W[k.id]]
                )
                == 1
                , name=nameConstraint
            )
    def __addConstr_Alpha(self, customers: list[Customer], satellites: list[Satellite]):
        for s in satellites:
            for k in customers:
                if k.isSmall:
                    nameConstraint = f'R_alpha_s{s.id}_k{k.id}'
                    self.model.addConstr(
                        quicksum(
                            [k.demand * self.X[(s.id, k.id)]]
                        )
                        - quicksum(
                            [self.ALPHA[(s.id, k.id)]]
                        )
                        == 0
                        , name=nameConstraint
                    )
    def __addConstr_Beta(self, customers: list[Customer]):
        for k in customers:
            if k.isSmall:
                continue
            nameConstraint = f'R_beta_k{k.id}'
            self.model.addConstr(
                quicksum(
                    [k.demand * self.W[k.id]]
                )
                - quicksum(
                    [self.BETA[k.id]]
                )
                == 0
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
