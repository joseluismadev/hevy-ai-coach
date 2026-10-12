"""Descarga tus entrenamientos de Hevy a data/hevy_workouts.json.

Uso:
    python -m src.download_workouts
"""

from .config import HEVY_WORKOUTS_PATH
from .hevy_client import fetch_all_workouts, save_workouts


def main() -> None:
    workouts = fetch_all_workouts()
    save_workouts(workouts)

    print(f"Descargados {len(workouts)} entrenamientos en {HEVY_WORKOUTS_PATH}")
    if workouts:
        last = workouts[0]
        print(f"Último entrenamiento: {last.get('title')} ({last.get('start_time')})")


if __name__ == "__main__":
    main()
