from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, LpInteger


class Optimizer:
    """
    Linear Programming (LP) procurement optimizer.

    Cost includes:
    - unit cost per (supplier, material)
    - transport cost based on distance × cost per km per unit
    - product threshold penalties (max cost willing to pay per product)

    Constraints include:
    - product demand satisfaction (soft via z[p])
    - material procurement based on producible products
    - supplier capacity limits (hard constraint)
    """

    def __init__(self, dataset, transport_cost_per_km=0.001):
        self.dataset = dataset
        self.transport_cost_per_km = transport_cost_per_km

        self.model = None
        self.x = {}
        self.y = {}
        self.z = {}

    def build_model(self):

        products = self.dataset.get_products()
        materials = self.dataset.get_materials()
        suppliers = self.dataset.get_suppliers()

        self.model = LpProblem("Procurement_Optimization", LpMinimize)

        # -----------------------------
        # Decision variables
        # -----------------------------
        for p in products:
            demand_p = self.dataset.get_demand(p)
            self.y[p] = LpVariable(
                f"y_{p}",
                lowBound=0,
                upBound=demand_p,
                cat=LpInteger
            )
            self.z[p] = LpVariable(
                f"z_{p}",
                lowBound=0,
                cat=LpInteger
            )

        for s in suppliers:
            for m in materials:
                self.x[(s, m)] = LpVariable(
                    f"x_{s}_{m}",
                    lowBound=0
                )

        # -----------------------------
        # COST FUNCTION
        # -----------------------------
        procurement_cost = lpSum(
            self.dataset.get_unit_cost(s, m) * self.x[(s, m)]
            for s in suppliers for m in materials
        )

        transport_cost = lpSum(
            self.transport_cost_per_km * self.dataset.get_supplier_distance(s) * lpSum(self.x[(s, m)] for m in materials)
            for s in suppliers
        )

        shortage_cost = lpSum(
            self.dataset.get_threshold(p) * self.z[p]
            for p in products
        )

        self.model += procurement_cost + transport_cost + shortage_cost

        # -----------------------------
        # CONSTRAINTS
        # -----------------------------

        # (1) Product demand constraints (soft via z[p])
        for p in products:
            demand_p = self.dataset.get_demand(p)
            self.model += (
                self.y[p] + self.z[p] == demand_p,
                f"demand_{p}"
            )

        # (2) Material procurement constraints (based on producible products)
        for m in materials:
            required = lpSum(
                self.y[p] * self.dataset.get_ingredients_per_product(p).get(m, 0)
                for p in products
            )
            self.model += (
                lpSum(self.x[(s, m)] for s in suppliers) >= required,
                f"material_{m}"
            )

        # (3) Capacity constraints (HARD)
        for s in suppliers:
            for m in materials:
                capacity = self.dataset.get_supplier_capacity(s, m)

                self.model += (
                    self.x[(s, m)] <= capacity,
                    f"capacity_{s}_{m}"
                )

        return self.model

    def solve(self):

        if self.model is None:
            raise Exception("Model not built. Call build_model() first.")

        self.model.solve()
        return self.get_solution()

    def get_solution(self):

        solution = {
            "status": LpStatus[self.model.status],
            "objective_value": self.model.objective.value(),
            "procurement": {},
            "shortages": {},
            "production": {}
        }

        for (s, m), var in self.x.items():
            val = var.value()
            if val and val > 1e-6:
                solution["procurement"][(s, m)] = val

        for p, var in self.z.items():
            val = var.value()
            if val and val > 0:
                solution["shortages"][p] = val

        for p, var in self.y.items():
            val = var.value()
            if val and val > 0:
                solution["production"][p] = val

        return solution