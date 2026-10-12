"""Métricas de entrenamiento que se le pasan al coach de IA.

Regla de oro: el código calcula, el LLM interpreta. Los LLM se equivocan haciendo
cuentas sobre miles de filas, así que les damos un resumen pequeño y ya calculado.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

# Referencia orientativa para hipertrofia: series efectivas por músculo y semana
SETS_PER_WEEK_RANGE = (10, 20)
# Sesiones más largas se consideran olvidadas abiertas en Hevy
MAX_SESSION_MINUTES = 240
# Cambio mínimo (%) entre el inicio y el final del periodo para considerar que hay tendencia
TREND_THRESHOLD_PCT = 2.0
MIN_SESSIONS_FOR_TREND = 4


def _sets_status(sets_per_week: float) -> str:
    low, high = SETS_PER_WEEK_RANGE
    if sets_per_week < low:
        return "bajo"
    if sets_per_week > high:
        return "alto"
    return "en rango"


def _trend_status(change_pct: float) -> str:
    if change_pct > TREND_THRESHOLD_PCT:
        return "progresando"
    if change_pct < -TREND_THRESHOLD_PCT:
        return "retrocediendo"
    return "estancado"


def muscle_volume(period: pd.DataFrame, all_muscles: List[str], weeks: int) -> List[Dict[str, Any]]:
    """Series por semana de cada músculo, incluyendo los que no se han entrenado en el periodo."""
    counts = period.groupby("muscle_group").size().reindex(all_muscles, fill_value=0)
    result = []
    for muscle, total in counts.sort_values(ascending=False).items():
        per_week = round(total / weeks, 1)
        result.append({"musculo": muscle, "series_por_semana": per_week, "estado": _sets_status(per_week)})
    return result


def exercise_trends(period: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compara las primeras y las últimas sesiones del periodo de cada ejercicio.

    Con peso se usa el 1RM estimado; con peso corporal, las repeticiones máximas.
    """
    trends = []
    for exercise, group in period.groupby("exercise"):
        weighted = group["weight_kg"].notna().any()
        metric = "e1rm_kg" if weighted else "reps"
        per_session = group.groupby("start_time")[metric].max().sort_index()

        if len(per_session) < MIN_SESSIONS_FOR_TREND:
            continue

        k = min(3, len(per_session) // 2)
        first = float(per_session.iloc[:k].mean())
        last = float(per_session.iloc[-k:].mean())
        change_pct = (last - first) / first * 100 if first else 0.0

        # Mejor serie de la última sesión: el peso real con el que entrenas, no el 1RM estimado
        last_session = group[group["start_time"] == per_session.index[-1]]
        best_set = last_session.loc[last_session[metric].idxmax()]

        trends.append(
            {
                "ejercicio": exercise,
                "musculo": group["muscle_group"].iloc[0],
                "metrica": "1RM estimado (kg)" if weighted else "repeticiones máximas",
                "sesiones": len(per_session),
                "inicio": round(first, 1),
                "final": round(last, 1),
                "cambio_pct": round(change_pct, 1),
                "estado": _trend_status(change_pct),
                "ultima_serie": {
                    "peso_kg": float(best_set["weight_kg"]) if weighted else None,
                    "reps": int(best_set["reps"]),
                },
            }
        )

    return sorted(trends, key=lambda t: t["sesiones"], reverse=True)


def build_training_summary(
    df: pd.DataFrame, weeks: int = 8, end: Optional[pd.Timestamp] = None
) -> Dict[str, Any]:
    """Resumen compacto de las últimas `weeks` semanas, listo para pasárselo a un LLM."""
    work = df[~df["is_warmup"]]
    end = end if end is not None else work["start_time"].max()
    start = end - pd.Timedelta(weeks=weeks)
    period = work[(work["start_time"] > start) & (work["start_time"] <= end)]

    sessions = period.groupby("workout_id").agg(
        title=("workout_title", "first"), start=("start_time", "first"), end=("end_time", "first")
    )
    minutes = (sessions["end"] - sessions["start"]).dt.total_seconds() / 60
    valid_minutes = minutes[minutes <= MAX_SESSION_MINUTES]

    return {
        "periodo": {
            "desde": str(start.date()),
            "hasta": str(end.date()),
            "semanas": weeks,
        },
        "frecuencia": {
            "sesiones": len(sessions),
            "sesiones_por_semana": round(len(sessions) / weeks, 1),
            "duracion_mediana_min": round(valid_minutes.median()) if len(valid_minutes) else None,
            "rutinas": sessions["title"].value_counts().to_dict(),
        },
        "referencia_series_semana": list(SETS_PER_WEEK_RANGE),
        "nota": (
            "Cada serie cuenta solo para el músculo principal del ejercicio; "
            "los músculos secundarios (p. ej. bíceps en un remo) también reciben trabajo indirecto."
        ),
        "series_por_musculo": muscle_volume(period, sorted(work["muscle_group"].unique()), weeks),
        "tendencias_ejercicios": exercise_trends(period),
    }
