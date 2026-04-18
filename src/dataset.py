import random


class DatasetInterface:
    """
    Mock dataset for procurement optimization (LP version).

    Provides:
    - product demand
    - BOM structure
    - unit cost per (supplier, material)
    - supplier distances (for transport cost)
    - supplier capacities
    """

    def __init__(self, seed=42):
        random.seed(seed)

        # ------------------------
        # CORE ENTITIES
        # ------------------------
        self._products = ["cola", "juice", "water"]
        self._materials = ["sugar", "water", "flavoring", "bottle", "label"]
        self._suppliers = ["s1", "s2", "s3", "s4"]

        # ------------------------
        # DEMAND
        # ------------------------
        self._demand = {
            "cola": 1000,
            "juice": 800,
            "water": 1200
        }

        # ------------------------
        # THRESHOLD COST PER PRODUCT
        # ------------------------
        self._threshold = {
            "cola": 20.0,
            "juice": 15.0,
            "water": 10.0
        }

        # ------------------------
        # BILL OF MATERIALS
        # ------------------------
        self._bom = {
            "cola": {
                "sugar": 0.5,
                "water": 0.2,
                "flavoring": 1.5,
                "bottle": 0.1,
                "label": 0.1
            },
            "juice": {
                "sugar": 0.9,
                "water": 0.1,
                "flavoring": 0.5,
                "bottle": 0.9,
                "label": 0.1
            },
            "water": {
                "water": 0.1,
                "bottle": 0.2,
                "label": 0.5
            }
        }

        # ------------------------
        # UNIT COST per (supplier, material)
        # ------------------------
        self._unit_cost = {
            (s, m): round(random.uniform(0.5, 6.0), 2)
            for s in self._suppliers
            for m in self._materials
        }

        # ------------------------
        # DISTANCE per supplier (km)
        # ------------------------
        self._distance = {
            "s1": random.randint(150, 1000),
            "s2": random.randint(150, 1000),
            "s3": random.randint(150, 1000),
            "s4": random.randint(150, 1000)
        }

        # ------------------------
        # CAPACITY per (supplier, material)
        # ------------------------
        self._capacity = {
            (s, m): random.randint(50, 150)
            for s in self._suppliers
            for m in self._materials
        }

    # =========================================================
    # BASIC ACCESS METHODS
    # =========================================================

    def get_products(self):
        return self._products

    def get_materials(self):
        return self._materials

    def get_suppliers(self):
        return self._suppliers

    def get_demand(self, product):
        return self._demand[product]

    def get_threshold(self, product):
        return self._threshold[product]

    def get_ingredients_per_product(self, product):
        return self._bom[product]

    # =========================================================
    # COST MODEL (UPDATED)
    # =========================================================

    def get_unit_cost(self, supplier, material):
        """
        Cost per unit of material from a supplier.
        """
        return self._unit_cost[(supplier, material)]

    def get_supplier_distance(self, supplier):
        """
        Distance from supplier to company (km).
        Used for transport cost:
            transport_cost = distance × cost_per_km × quantity
        """
        return self._distance[supplier]

    # =========================================================
    # CAPACITY
    # =========================================================

    def get_supplier_capacity(self, supplier, material):
        """
        Max supply of a material from a supplier.
        """
        return self._capacity[(supplier, material)]