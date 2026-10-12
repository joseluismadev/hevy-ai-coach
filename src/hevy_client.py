"""Cliente para la API pública de Hevy (requiere Hevy Pro).

Documentación: https://api.hevyapp.com/docs
La autenticación se hace con la cabecera `api-key`, no con `Authorization: Bearer`.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import requests

from .config import HEVY_API_KEY, HEVY_API_URL, HEVY_WORKOUTS_PATH, SAMPLE_WORKOUTS_PATH

# Tamaño máximo de página que acepta Hevy en cada endpoint
WORKOUTS_PAGE_SIZE = 10
TEMPLATES_PAGE_SIZE = 100


def load_sample_workouts(path: Path = SAMPLE_WORKOUTS_PATH) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _fetch_paginated(
    endpoint: str, items_key: str, page_size: int, api_key: str, base_url: str
) -> List[Dict[str, Any]]:
    """Recorre todas las páginas de un endpoint de Hevy y junta los resultados."""
    if not api_key:
        raise RuntimeError("Falta HEVY_API_KEY. Añádela a tu archivo .env")

    headers = {"api-key": api_key, "accept": "application/json"}
    items: List[Dict[str, Any]] = []
    page = 1

    while True:
        response = requests.get(
            f"{base_url}{endpoint}",
            headers=headers,
            params={"page": page, "pageSize": page_size},
            timeout=15,
        )
        # Hevy responde 404 cuando pides una página que no existe (p. ej. si no hay datos)
        if response.status_code == 404:
            break
        response.raise_for_status()

        data = response.json()
        items.extend(data.get(items_key, []))

        if page >= data.get("page_count", 0):
            break
        page += 1

    return items


def fetch_all_workouts(api_key: str = HEVY_API_KEY, base_url: str = HEVY_API_URL) -> List[Dict[str, Any]]:
    """Descarga todos tus entrenamientos (/v1/workouts)."""
    return _fetch_paginated("/v1/workouts", "workouts", WORKOUTS_PAGE_SIZE, api_key, base_url)


def fetch_exercise_templates(api_key: str = HEVY_API_KEY, base_url: str = HEVY_API_URL) -> List[Dict[str, Any]]:
    """Descarga el catálogo de ejercicios (/v1/exercise_templates), que incluye el grupo muscular."""
    return _fetch_paginated(
        "/v1/exercise_templates", "exercise_templates", TEMPLATES_PAGE_SIZE, api_key, base_url
    )


def save_json(items: List[Dict[str, Any]], path: Path = HEVY_WORKOUTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)
