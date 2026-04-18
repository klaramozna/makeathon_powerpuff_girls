# makeathon_powerpuff_girls

Simple Python app to visualize company-specific data from `db.sqlite`.

## Stack

- Python
- Streamlit (UI)
- SQLite (data source)

## App features

- Start page with company selection dropdown
- Two tabs per company:
  - `Products`
  - `Raw Materials`
- Lightweight, modern table-based UI

## Project structure

```text
app/
  __init__.py
  config.py
  db.py
  main.py
requirements.txt
db.sqlite
```

## 1) Clone and open project

```bash
git clone <your-repo-url>
cd makeathon_powerpuff_girls
```

## 2) Add `.gitignore` entries (important)

If `.gitignore` does not exist, create it at the project root and add at least:

```gitignore
db.sqlite
.venv/
__pycache__/
.pytest_cache/
*.pyc
```

Why:
- `db.sqlite` can contain local/private data and usually should not be committed.
- `.venv` and cache files are machine-specific build artifacts.

## 3) Prepare the database file

The app expects the database here:

```text
./db.sqlite
```

If your DB is somewhere else, copy it into the project root with the exact name `db.sqlite`.

## 4) Create and activate Python environment

Recommended Python version: 3.11+ (3.13 also works).

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 5) Install dependencies

```bash
pip install -r requirements.txt
```

Optional check:

```bash
python -m pip list
```

## 6) Run the app

Default (recommended for local dev):

```bash
streamlit run app/main.py
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
