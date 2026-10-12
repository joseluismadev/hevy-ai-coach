from fastapi import FastAPI, HTTPException, Query

from .analytics import generate_recommendation, muscle_distribution, summarize_workouts
from .coach import generate_coach_report
from .config import HEVY_WORKOUTS_PATH
from .dataset import load_sets_df
from .hevy_client import load_sample_workouts
from .metrics import build_training_summary

app = FastAPI(title="Hevy AI Coach", version="0.2.0")


def _training_summary(weeks: int) -> dict:
    if not HEVY_WORKOUTS_PATH.exists():
        raise HTTPException(404, "No hay datos de Hevy. Ejecuta: python -m src.download_workouts")
    return build_training_summary(load_sets_df(), weeks=weeks)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "message": "Hevy AI Coach está activo"}


@app.get("/workouts")
def get_workouts() -> dict:
    # Endpoint de la primera versión, con datos de ejemplo en formato simplificado
    workouts = load_sample_workouts()
    return {
        "count": len(workouts),
        "summary": summarize_workouts(workouts),
        "muscle_distribution": muscle_distribution(workouts),
        "recommendation": generate_recommendation(workouts),
    }


@app.get("/metrics")
def get_metrics(weeks: int = Query(8, ge=1, le=52)) -> dict:
    """Métricas calculadas de tus entrenamientos reales (sin LLM)."""
    return _training_summary(weeks)


@app.get("/coach")
def get_coach(weeks: int = Query(8, ge=1, le=52)) -> dict:
    """Informe del coach de IA a partir de tus métricas."""
    summary = _training_summary(weeks)
    try:
        report = generate_coach_report(summary)
    except Exception as error:
        raise HTTPException(502, f"Error al consultar el LLM: {error}") from error
    return {"report": report.model_dump(), "metrics": summary}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
