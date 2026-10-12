from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def compute_session_volume(session: Dict[str, Any]) -> float:
    total = 0.0
    for exercise in session.get("exercises", []):
        weight = float(exercise.get("weight_kg", 0) or 0)
        reps = float(exercise.get("reps", 0) or 0)
        sets = float(exercise.get("sets", 0) or 0)
        total += weight * reps * sets
    return round(total, 2)


def summarize_workouts(workouts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summary = []
    for workout in workouts:
        total_volume = compute_session_volume(workout)
        summary.append(
            {
                "date": workout.get("date"),
                "workout_name": workout.get("workout_name"),
                "exercise_count": len(workout.get("exercises", [])),
                "total_volume": total_volume,
            }
        )
    return summary


def muscle_distribution(workouts: List[Dict[str, Any]]) -> Dict[str, float]:
    totals: Dict[str, float] = defaultdict(float)
    for workout in workouts:
        for exercise in workout.get("exercises", []):
            muscle = exercise.get("muscle_group", "Unknown")
            weight = float(exercise.get("weight_kg", 0) or 0)
            reps = float(exercise.get("reps", 0) or 0)
            sets = float(exercise.get("sets", 0) or 0)
            totals[muscle] += weight * reps * sets

    return {key: round(value, 2) for key, value in sorted(totals.items())}


def generate_recommendation(workouts: List[Dict[str, Any]]) -> str:
    if not workouts:
        return "Aún no hay datos suficientes para hacer una recomendación."

    total_volume = sum(compute_session_volume(session) for session in workouts)
    summary = summarize_workouts(workouts)
    active_muscles = muscle_distribution(workouts)
    top_muscle = max(active_muscles.items(), key=lambda item: item[1])[0]
    heaviest = max(summary, key=lambda item: item["total_volume"])

    return (
        f"Tu volumen total acumulado es {total_volume}. "
        f"El músculo más cargado en este bloque es {top_muscle}. "
        f"Revisa la sesión con más carga: {heaviest['workout_name']} el {heaviest['date']}. "
        "Sigue aumentando el volumen progresivamente y añade una pequeña variación de intensidad cada 2-3 semanas."
    )
