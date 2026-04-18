# Procurement Optimization

Linear programming-based optimizer for procurement planning, ensuring whole products are built rather than partial materials.

## Features

- Optimizes material procurement from suppliers with cost and transport considerations.
- Handles product-level shortages to avoid partial product builds.
- Uses integer constraints for exact product quantities.

## Project Structure

```
src/
  dataset.py    # Mock data interface
  main.py       # Entry point for optimization
  optimizer.py  # LP model implementation
requirements.txt
```

## Setup

1. Create virtual environment:
   ```bash
   python -m venv .venv
   # Activate: source .venv/bin/activate (Linux/macOS) or .venv\Scripts\Activate.ps1 (Windows)
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run optimization:
   ```bash
   python src/main.py
   ```

If port `8501` is busy, choose another port:

```bash
streamlit run app/main.py --server.port 8511
```

`--server.headless true` is optional and mainly useful on remote/server environments.

## 7) Stop the app

In the terminal where Streamlit is running, press:

```text
Ctrl + C
```

## 8) Run the optimizer
```bash
cd src
python optimizer.py
```

## Common issues

### `command not found: streamlit`

Your virtual environment is likely not active.

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `No such table` / DB errors

Make sure `db.sqlite` exists in the root folder and has the expected schema.

### Wrong command typo

Use:

```bash
streamlit run app/main.py
```

not `streamlit run app/main.`

## Optional: freeze exact dependency versions

If you want fully reproducible installs:

```bash
pip freeze > requirements.lock.txt
```

## 🧠 Optimizer

### Input
The optimizer takes structured supply chain data:
- Products and their demand (units to be produced)
- Bill of Materials (BOM): material requirements per product
- Materials (raw ingredients / packaging items)
- Suppliers
- Unit cost per supplier per material
- Distance of company to supplier
- Supplier capacity per material
- Threshold cost per product (max possible price we want to pay to make it)
- Cost per distance per unit

---

### Output
The model returns:
- Optimal procurement plan: quantity of each material to buy from each supplier
- Production plan: number of each product to produce
- Product shortages (if demand cannot be fully met due to cost thresholds or constraints)
- Total optimized cost (including threshold penalties for shortages)

---

### Optimization Model
The problem is formulated as a **Mixed Integer Linear Programming (MILP)** model.

It minimizes total cost:

- Procurement cost: sum of (supplier cost + transport cost) × quantity purchased
- Shortage penalty: threshold cost per product for unmet demand

Subject to:
- Product demand constraints (can be partially violated via penalties)
- Material procurement based on producible products
- Supplier capacity constraints

Shortage variables are introduced per product to ensure feasibility. Products are produced only if the marginal cost is below the threshold.

---

### Key Assumptions
- Distance cost is 0.05 euros per km per unit
- Materials are divisible (continuous quantities)
- Products are produced in whole units (integer constraints)
- Supplier capacities are fixed and known
- Demand is deterministic (no uncertainty)
- Shortages at product level if cost exceeds threshold
- No transportation or time constraints included

### 💻 Output Usage in Code

The optimizer returns a dictionary called `solution` with four fields:

---

**1. status (str)**  
Indicates the result of the optimization run.

Possible values:
- `"Optimal"` → A valid best solution was found
- `"Infeasible"` → No solution satisfies constraints
- `"Unbounded"` → Cost can be reduced indefinitely
- `"Not Solved"` → Solver did not run properly

Meaning: tells you whether the result can be trusted.

---

**2. objective_value (float)**  
The total minimized cost of the solution.

Includes:
- procurement cost (what you pay suppliers)
- shortage penalties (cost for unmet demand)

Meaning: lower value = better solution.

---

**3. procurement (Dict[(str, str), float])**  
Maps `(supplier, material)` → quantity purchased.

Example:
`("s1", "sugar") → 500`

Meaning:
How much of each material to buy from each supplier.

If a pair is missing, its value is 0 or negligible.

---

**4. shortages (Dict[str, float])**  
Maps `product → unmet demand`.

Possible values:
- empty `{}` → all demand fully satisfied
- positive float → number of missing products

Meaning:
Shows products not produced due to cost exceeding threshold or constraints.

---

**5. production (Dict[str, float])**  
Maps `product → quantity produced`.

Meaning:
Number of each product to manufacture.

Usage in code:

```python
solution = {
    "status": str,
    "objective_value": float,
    "procurement": Dict[Tuple[str, str], float],
    "shortages": Dict[str, float],
    "production": Dict[str, float]
}

solution = optimizer.solve()

# Solver status
print(solution["status"])

# Total optimized cost
print(solution["objective_value"])

# Procurement plan: (supplier, material) -> quantity
for (supplier, material), qty in solution["procurement"].items():
    print(supplier, material, qty)

# Production plan: product -> quantity
for product, qty in solution["production"].items():
    print(product, qty)

# Product shortages
for product, missing_qty in solution["shortages"].items():
    print(product, missing_qty)

# Optional: disable console output in pipeline usage
run_optimization(verbose=False)
```
