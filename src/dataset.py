import sqlite3
from pathlib import Path


class DatasetInterface:
    """
    Database-backed dataset for procurement optimization.

    Loads company-specific finished goods, raw materials,
    BOM amounts, supplier distances, supplier material costs,
    and capacities from `db_new.sqlite`.
    """

    def __init__(self, company_id=1, db_path=None):
        self.company_id = company_id
        self.db_path = Path(db_path) if db_path else Path(__file__).resolve().parents[1] / "db_new.sqlite"

        self.company_name = None
        self._products = []
        self._materials = []
        self._suppliers = []
        self._demand = {}
        self._threshold = {}
        self._bom = {}
        self._unit_cost = {}
        self._capacity = {}
        self._distance = {}
        self._supplier_material_pairs = []

        self._load_data()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _load_data(self):
        with self._connect() as connection:
            cursor = connection.cursor()

            company_row = cursor.execute(
                "SELECT Name FROM Company WHERE Id = ?",
                (self.company_id,)
            ).fetchone()
            if company_row is None:
                raise ValueError(f"Company id {self.company_id} not found in {self.db_path}")
            self.company_name = company_row["Name"]

            finished_rows = cursor.execute(
                "SELECT Id, SKU, Demand, Threshold "
                "FROM Product "
                "WHERE CompanyId = ? AND Type = 'finished-good' "
                "ORDER BY Id",
                (self.company_id,)
            ).fetchall()
            if not finished_rows:
                raise ValueError(f"No finished goods found for company id {self.company_id}")

            for row in finished_rows:
                sku = row["SKU"]
                self._products.append(sku)
                self._demand[sku] = row["Demand"] or 0
                self._threshold[sku] = row["Threshold"] or 0

            material_rows = cursor.execute(
                "SELECT DISTINCT rm.Id, rm.SKU "
                "FROM BOM_Component bc "
                "JOIN BOM b ON bc.BOMId = b.Id "
                "JOIN Product fg ON fg.Id = b.ProducedProductId "
                "JOIN Product rm ON rm.Id = bc.ConsumedProductId "
                "WHERE fg.CompanyId = ? AND fg.Type = 'finished-good' "
                "AND rm.Type = 'raw-material' "
                "ORDER BY rm.Id",
                (self.company_id,)
            ).fetchall()
            if not material_rows:
                raise ValueError(f"No raw materials found for company id {self.company_id}")

            for row in material_rows:
                self._materials.append(row["SKU"])

            self._bom = {sku: {} for sku in self._products}
            bom_rows = cursor.execute(
                "SELECT fg.SKU AS product_sku, rm.SKU AS material_sku, bc.Amount "
                "FROM BOM_Component bc "
                "JOIN BOM b ON b.Id = bc.BOMId "
                "JOIN Product fg ON fg.Id = b.ProducedProductId "
                "JOIN Product rm ON rm.Id = bc.ConsumedProductId "
                "WHERE fg.CompanyId = ? AND fg.Type = 'finished-good' "
                "AND rm.Type = 'raw-material'",
                (self.company_id,)
            ).fetchall()
            for row in bom_rows:
                self._bom[row["product_sku"]][row["material_sku"]] = row["Amount"] or 0.0

            if self._materials:
                placeholders = ",".join("?" for _ in self._materials)
                supplier_rows = cursor.execute(
                    f"SELECT DISTINCT s.Id, s.Name, s.DistanceKm "
                    f"FROM Supplier s "
                    f"JOIN Supplier_Product sp ON sp.SupplierId = s.Id "
                    f"JOIN Product rm ON rm.Id = sp.ProductId "
                    f"WHERE rm.Type = 'raw-material' AND rm.SKU IN ({placeholders}) "
                    f"ORDER BY s.Id",
                    tuple(self._materials)
                ).fetchall()

                for row in supplier_rows:
                    self._suppliers.append(row["Name"])
                    self._distance[row["Name"]] = row["DistanceKm"] or 0.0

                pair_rows = cursor.execute(
                    f"SELECT s.Name AS supplier, rm.SKU AS material, sp.UnitCost, sp.Capacity "
                    f"FROM Supplier_Product sp "
                    f"JOIN Supplier s ON s.Id = sp.SupplierId "
                    f"JOIN Product rm ON rm.Id = sp.ProductId "
                    f"WHERE rm.Type = 'raw-material' AND rm.SKU IN ({placeholders}) "
                    f"ORDER BY s.Id, rm.Id",
                    tuple(self._materials)
                ).fetchall()

                for row in pair_rows:
                    supplier_name = row["supplier"]
                    material_name = row["material"]
                    self._supplier_material_pairs.append((supplier_name, material_name))
                    self._unit_cost[(supplier_name, material_name)] = row["UnitCost"] or 0.0
                    self._capacity[(supplier_name, material_name)] = row["Capacity"] or 0

            if not self._suppliers or not self._supplier_material_pairs:
                raise ValueError(
                    f"No supplier-material relationships found for company id {self.company_id}"
                )

    def get_company_name(self):
        return self.company_name

    def get_products(self):
        return self._products

    def get_materials(self):
        return self._materials

    def get_suppliers(self):
        return self._suppliers

    def get_supplier_material_pairs(self):
        return self._supplier_material_pairs

    def get_demand(self, product):
        return self._demand[product]

    def get_threshold(self, product):
        return self._threshold[product]

    def get_ingredients_per_product(self, product):
        return self._bom[product]

    def get_unit_cost(self, supplier, material):
        return self._unit_cost[(supplier, material)]

    def get_supplier_distance(self, supplier):
        return self._distance[supplier]

    def get_supplier_capacity(self, supplier, material):
        return self._capacity[(supplier, material)]
