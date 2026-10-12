"""Cliente para la API pública de Hevy (requiere Hevy Pro).

Documentación: https://api.hevyapp.com/docs
La autenticación se hace con la cabecera `api-key`, no con `Authorization: Bearer`.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import requests

from .config import HEVY_API_KEY, HEVY_API_URL, HEVY_WORKOUTS_PATH, SAMPLE_WORKOUTS_PATH

# Hevy devuelve como máximo 10 entrenamientos por página
PAGE_SIZE = 10


def load_sample_workouts(path: Path = SAMPLE_WORKOUTS_PATH) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def fetch_all_workouts(api_key: str = HEVY_API_KEY, base_url: str = HEVY_API_URL) -> List[Dict[str, Any]]:
    """Descarga todos los entrenamientos recorriendo las páginas de /v1/workouts."""
    if not api_key:
        raise RuntimeError("Falta HEVY_API_KEY. Añádela a tu archivo .env")

    headers = {"api-key": api_key, "accept": "application/json"}
    workouts: List[Dict[str, Any]] = []
    page = 1

    while True:
        response = requests.get(
            f"{base_url}/v1/workouts",
            headers=headers,
            params={"page": page, "pageSize": PAGE_SIZE},
            timeout=15,
        )
        # Hevy responde 404 cuando pides una página que no existe (p. ej. si no tienes entrenamientos)
        if response.status_code == 404:
            break
        response.raise_for_status()

        data = response.json()
        workouts.extend(data.get("workouts", []))

        if page >= data.get("page_count", 0):
            break
        page += 1

    return workouts


def save_workouts(workouts: List[Dict[str, Any]], path: Path = HEVY_WORKOUTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(workouts, file, ensure_ascii=False, indent=2)
