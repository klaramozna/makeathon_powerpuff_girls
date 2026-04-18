import sqlite3
from contextlib import closing

from .config import DATABASE_PATH


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_companies() -> list[dict]:
    query = """
        SELECT Id, Name
        FROM Company
        ORDER BY Name;
    """
    with closing(_connect()) as connection:
        rows = connection.execute(query).fetchall()
    return [dict(row) for row in rows]


def get_finished_goods(company_id: int) -> list[dict]:
    query = """
        SELECT
            p.Id,
            p.SKU,
            p.Type,
            COUNT(bc.ConsumedProductId) AS raw_material_count
        FROM Product p
        LEFT JOIN BOM b ON b.ProducedProductId = p.Id
        LEFT JOIN BOM_Component bc ON bc.BOMId = b.Id
        WHERE p.CompanyId = ?
          AND p.Type = 'finished-good'
        GROUP BY p.Id, p.SKU, p.Type
        ORDER BY p.SKU;
    """
    with closing(_connect()) as connection:
        rows = connection.execute(query, (company_id,)).fetchall()
    return [dict(row) for row in rows]


def get_raw_materials(company_id: int) -> list[dict]:
    query = """
        SELECT
            p.Id,
            p.SKU,
            p.Type,
            COUNT(sp.SupplierId) AS supplier_count
        FROM Product p
        LEFT JOIN Supplier_Product sp ON sp.ProductId = p.Id
        WHERE p.CompanyId = ?
          AND p.Type = 'raw-material'
        GROUP BY p.Id, p.SKU, p.Type
        ORDER BY p.SKU;
    """
    with closing(_connect()) as connection:
        rows = connection.execute(query, (company_id,)).fetchall()
    return [dict(row) for row in rows]
