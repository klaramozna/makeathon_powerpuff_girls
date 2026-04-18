from dataset import DatasetInterface
from optimizer import Optimizer


def run_optimization():
    """
    Runs the full procurement optimization pipeline:

    1. Loads dataset (mock or future SQL-backed)
    2. Builds LP optimization model
    3. Solves for optimal procurement plan
    4. Prints structured results
    """

    # -----------------------------
    # 1. Load dataset for a single company
    # -----------------------------
    dataset = DatasetInterface(company_id=1)

    # -----------------------------
    # 2. Initialize optimizer
    # -----------------------------
    optimizer = Optimizer(
        dataset=dataset
    )

    print(f"Running optimization for company: {dataset.get_company_name()}")

    # -----------------------------
    # 3. Build optimization model
    # -----------------------------
    optimizer.build_model()

    # -----------------------------
    # 4. Solve LP
    # -----------------------------
    solution = optimizer.solve()

    # -----------------------------
    # 5. Display results
    # -----------------------------
    print("\n==============================")
    print(" PROCUREMENT OPTIMIZATION RESULT")
    print("==============================\n")

    print("Status:", solution["status"])
    print("Total Cost:", solution["objective_value"])

    print("\n--- Procurement Plan ---")
    for (supplier, material), qty in solution["procurement"].items():
        print(f"{supplier} -> {material}: {round(qty, 2)}")

    print("\n--- Production Plan ---")
    for product, qty in solution["production"].items():
        print(f"{product}: {round(qty, 0)}")

    print("\n--- Shortages ---")
    if solution["shortages"]:
        for product, qty in solution["shortages"].items():
            print(f"{product}: {round(qty, 0)}")
    else:
        print("No shortages 🎉")




if __name__ == "__main__":
    run_optimization()