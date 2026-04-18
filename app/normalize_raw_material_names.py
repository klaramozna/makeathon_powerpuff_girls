import sqlite3
from typing import Dict, List

DB_PATH = "app/db.sqlite"

def normalize_raw_material_names(synonym_map: Dict[str, List[str]], canonical_map: Dict[str, str]):
    """
    For each group of synonyms, update all Product SKUs and references to the canonical name.
    synonym_map: {canonical_name: [variant1, variant2, ...], ...}
    canonical_map: {variant: canonical_name, ...} (for quick lookup)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update Product SKUs to canonical names
    for canonical, variants in synonym_map.items():
        for variant in variants:
            cursor.execute(
                """
                UPDATE Product SET SKU = ? WHERE SKU = ?
                """, (canonical, variant)
            )

    # If BOM_Component or other tables reference by SKU, update them here as needed
    # (Assumes BOM_Component uses Product.Id, so no SKU update needed there)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Example usage
    synonym_map = {
        "vitamin-c": ["vitamin-c", "ascorbic-acid", "vitamin-c-ascorbic-acid", "vitamin-c-l-ascorbic-acid", "ascorbic-acid-vitamin-c"],
        "magnesium-stearate": ["magnesium-stearate", "vegetable-magnesium-stearate"],
        "polyethylene-glycol": ["polyethylene-glycol"],
        "polyvinyl-alcohol": ["polyvinyl-alcohol"]
    }
    # Build a reverse lookup for quick mapping
    canonical_map = {v: k for k, vs in synonym_map.items() for v in vs}
    normalize_raw_material_names(synonym_map, canonical_map)
    print("Normalization complete.")
