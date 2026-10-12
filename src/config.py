import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

HEVY_API_URL = os.getenv("HEVY_API_URL", "https://api.hevyapp.com")
HEVY_API_KEY = os.getenv("HEVY_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SAMPLE_WORKOUTS_PATH = DATA_DIR / "sample_workouts.json"
# Aquí se guardan tus entrenamientos reales descargados de Hevy (no se sube a git)
HEVY_WORKOUTS_PATH = DATA_DIR / "hevy_workouts.json"
