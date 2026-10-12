from fastapi import FastAPI

from .analytics import generate_recommendation, muscle_distribution, summarize_workouts
from .hevy_client import load_sample_workouts

app = FastAPI(title="Hevy AI Coach", version="0.1.0")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "message": "Hevy AI Coach está activo"}


@app.get("/workouts")
def get_workouts() -> dict:
    # De momento usa los datos de ejemplo: el análisis aún espera el formato simplificado.
    # Cuando adaptemos analytics.py al formato real de Hevy, leerá data/hevy_workouts.json.
    workouts = load_sample_workouts()
    return {
        "count": len(workouts),
        "summary": summarize_workouts(workouts),
        "muscle_distribution": muscle_distribution(workouts),
        "recommendation": generate_recommendation(workouts),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
