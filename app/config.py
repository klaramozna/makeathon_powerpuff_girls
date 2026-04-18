import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "db.sqlite"


def _load_local_env() -> None:
	env_path = BASE_DIR / ".env"
	if not env_path.exists():
		return

	for raw_line in env_path.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, value = line.split("=", 1)
		key = key.strip()
		value = value.strip().strip('"').strip("'")
		os.environ.setdefault(key, value)


_load_local_env()

# Dify integration settings.
# Values are loaded from .env in the project root.
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
DIFY_USER_PREFIX = os.getenv("DIFY_USER_PREFIX", "company")

# Map these keys to your Dify workflow input variable names.
DIFY_INPUT_KEY_RAW_MATERIALS_LIST = "raw_materials"
