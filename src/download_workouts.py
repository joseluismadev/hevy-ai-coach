"""Descarga tus entrenamientos y el catálogo de ejercicios de Hevy a data/.

Uso:
    python -m src.download_workouts
"""

from .config import HEVY_TEMPLATES_PATH, HEVY_WORKOUTS_PATH
from .hevy_client import fetch_all_workouts, fetch_exercise_templates, save_json


def main() -> None:
    workouts = fetch_all_workouts()
    save_json(workouts, HEVY_WORKOUTS_PATH)
    print(f"Descargados {len(workouts)} entrenamientos en {HEVY_WORKOUTS_PATH}")
    if workouts:
        last = workouts[0]
        print(f"Último entrenamiento: {last.get('title')} ({last.get('start_time')})")

    templates = fetch_exercise_templates()
    save_json(templates, HEVY_TEMPLATES_PATH)
    print(f"Descargados {len(templates)} ejercicios en {HEVY_TEMPLATES_PATH}")


if __name__ == "__main__":
    main()
