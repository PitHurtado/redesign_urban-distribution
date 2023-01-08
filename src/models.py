# Gurobi
from classes import Segment, Satelite


class Model:

    def __init__(self, arce: dict[(str,str),any], nameModel = "Deterministic"):
        self.model = gb.Model(nameModel)
        # variables
        self.X = {}
        self.Y = {}
        self.W = {}

        #param arce
        self.arce = arce

        #objetive & metrics
        self.results = {}
        self.metrics = {}

    def build(self, segments: list[Segment], satelites: list[Satelite]):
        self.model.reset()
        # variables
        self.__addVariables(segments, satelites)
        # objective
        self.__addObjetive(segments, satelites)
        # constraints
        self.__addConstr_LocationSatelite()
        self.__addConstr_CapacitySatelite()
        self.__addConstr_DemandSatified()

    def __addVariables(self, segments: list[Segment], satelites: list[Satelite]):
        self.Y = dict(
            [((s.id,q), self.model.addVar(vtype=GRB.BINARY, name="Y_s%s_q%s" %(s.id,q))) for s in satelites for q in s.capacity.keys()]
        )
        self.X = dict(
            [((s.id,k.id), self.model.addVar(vtype=GRB.BINARY, name="X_s%s_k%s" %(s.id,k.id))) for s in satelites for k in segments]
        )
        self.W  = dict(
            [((k.id), self.model.addVar(vtype=GRB.BINARY, name="W_k%s" % (k.id))) for k in segments]
        )

    def __addObjective(self, segments: list[Segment], satelites: list[Satelite]):
        costLocation = quicksum(
            [s.costFixed[q]*self.Y[(s.id,q)] for s in satelites for q in s.capacity.keys()]
        )
        cost_2e = quicksum(
            [self.arce[(s_id,k.id)]["totalCost"]*self.X[(s_id,k.id)] for k in segments for s_id in k.setSateliteCoverage]
        )
        cost_1e = quicksum(
            [k.costServedFromDC*self.W[(k.id)] for k in segments]
        )
        costTotal = cost_1e + cost_2e + costLocation

        self.model.setObjective(costTotal, GRB.MINIMIZE)

    def __addConstr_LocationSatelite(self, satelites: list[Satelite]):
        for s in satelites:
            nameConstraint = "R_Open_s"+str(s.id)
            self.model.addConstr(
                quicksum([self.Y[(s.id,q)] for q in s.capacity.keys()]) <= 1
                , name=nameConstraint
            )

    def __addConstr_CapacitySatelite(self, satelites: list[Satelite]):
        for s in satelites:
            nameConstraint = "R_capacity_"+str(s.id)
            self.model.addConstr(
                quicksum(
                    [self.arce[(s.id,k_id)]['fleetSize']*self.X[(s.id,k_id)] for k_id in s.setSegmentCoverage]
                )
                - quicksum(
                    [s.numberVehiclesAvailable[q]*self.Y[(s.id,q)] for q in s.capacity.keys()]
                )
                <= 0
                , name=nameConstraint
            )

    def __addConstr_DemandSatified(self, segments: list[Segment]):
        for k in segments:
            nameConstraint = "R_Demand_k"+str(k.id)
            self.model.addConstr(
                quicksum(
                    [self.X[(s_id,k.id)] for s_id in k.setSateliteCoverage].append(self.W[(k.id)])
                )
                == 1
                , name=nameConstraint
            )

    def optimizeModel(self) -> str:
        self.model.optimize()
        return self.model.Status

    def showModel(self):
        self.model.display()

    def setParams(self, params: dict[str,int]):
        for key, item in params.items():
            self.model.setParam(key,item)