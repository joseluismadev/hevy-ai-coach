"""Convierte los entrenamientos de Hevy en un DataFrame con una fila por serie.

Trabajar a nivel de serie es la granularidad más fina que tenemos: a partir de ella
se puede agregar por ejercicio, sesión, semana o grupo muscular.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .config import HEVY_TEMPLATES_PATH, HEVY_WORKOUTS_PATH

# Las series de calentamiento no cuentan para medir progreso ni volumen efectivo
WARMUP_SET_TYPE = "warmup"
TIMEZONE = "Europe/Madrid"


def estimate_1rm(weight_kg: float, reps: float) -> float:
    """1RM estimado con la fórmula de Epley: peso * (1 + reps / 30).

    Permite comparar series con distinto peso y repeticiones (p. ej. 80x8 vs 90x5).
    Es poco fiable por encima de ~12 repeticiones.
    """
    if not weight_kg or not reps:
        return 0.0
    if reps == 1:
        return float(weight_kg)
    return round(weight_kg * (1 + reps / 30), 2)


def workouts_to_sets_df(
    workouts: List[Dict[str, Any]], templates: Optional[List[Dict[str, Any]]] = None
) -> pd.DataFrame:
    """Aplana la estructura entrenamiento -> ejercicio -> serie en una tabla."""
    muscle_by_template = {t["id"]: t.get("primary_muscle_group") for t in templates or []}
    rows = []

    for workout in workouts:
        for exercise in workout.get("exercises", []):
            template_id = exercise.get("exercise_template_id")
            for s in exercise.get("sets", []):
                rows.append(
                    {
                        "workout_id": workout.get("id"),
                        "workout_title": workout.get("title"),
                        "start_time": workout.get("start_time"),
                        "end_time": workout.get("end_time"),
                        "exercise": exercise.get("title"),
                        "exercise_template_id": template_id,
                        "muscle_group": muscle_by_template.get(template_id, "unknown"),
                        "set_index": s.get("index"),
                        "set_type": s.get("type"),
                        "weight_kg": s.get("weight_kg"),
                        "reps": s.get("reps"),
                        "rpe": s.get("rpe"),
                        "duration_seconds": s.get("duration_seconds"),
                        "distance_meters": s.get("distance_meters"),
                    }
                )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Hevy da las fechas en UTC; las pasamos a hora local para que el día sea el correcto
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True).dt.tz_convert(TIMEZONE)
    df["end_time"] = pd.to_datetime(df["end_time"], utc=True).dt.tz_convert(TIMEZONE)
    df["date"] = df["start_time"].dt.date
    # Semana = lunes de esa semana
    day = df["start_time"].dt.normalize()
    df["week"] = (day - pd.to_timedelta(day.dt.dayofweek, unit="D")).dt.date

    weight = df["weight_kg"].fillna(0).astype(float)
    reps = df["reps"].fillna(0).astype(float)
    df["volume_kg"] = weight * reps
    df["e1rm_kg"] = [estimate_1rm(w, r) for w, r in zip(weight, reps)]
    df["is_warmup"] = df["set_type"] == WARMUP_SET_TYPE

    return df.sort_values(["start_time", "exercise", "set_index"]).reset_index(drop=True)


def load_sets_df(
    workouts_path: Path = HEVY_WORKOUTS_PATH, templates_path: Path = HEVY_TEMPLATES_PATH
) -> pd.DataFrame:
    """Carga los JSON descargados con `python -m src.download_workouts` y devuelve el DataFrame."""
    with workouts_path.open("r", encoding="utf-8") as file:
        workouts = json.load(file)

    templates = None
    if templates_path.exists():
        with templates_path.open("r", encoding="utf-8") as file:
            templates = json.load(file)

    return workouts_to_sets_df(workouts, templates)
