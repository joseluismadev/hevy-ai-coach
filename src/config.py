import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

HEVY_API_URL = os.getenv("HEVY_API_URL", "https://api.hevyapp.com")
HEVY_API_KEY = os.getenv("HEVY_API_KEY", "")

# LLM: cualquier proveedor compatible con la API de OpenAI (Gemini, Groq, OpenAI...)
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")

SAMPLE_WORKOUTS_PATH = DATA_DIR / "sample_workouts.json"
# Aquí se guardan tus entrenamientos reales descargados de Hevy (no se sube a git)
HEVY_WORKOUTS_PATH = DATA_DIR / "hevy_workouts.json"
# Catálogo de ejercicios de Hevy: de aquí sale el grupo muscular de cada ejercicio
HEVY_TEMPLATES_PATH = DATA_DIR / "hevy_exercise_templates.json"
