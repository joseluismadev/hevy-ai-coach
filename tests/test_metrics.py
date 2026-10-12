from src.dataset import workouts_to_sets_df
from src.metrics import build_training_summary


def _workout(day, weight, reps, exercise="Press Banca", template="T1"):
    return {
        "id": f"w{day}",
        "title": "Empuje",
        "start_time": f"2026-09-{day:02d}T10:00:00+00:00",
        "end_time": f"2026-09-{day:02d}T11:30:00+00:00",
        "exercises": [
            {
                "title": exercise,
                "exercise_template_id": template,
                "sets": [{"index": 0, "type": "normal", "weight_kg": weight, "reps": reps}] * 3,
            }
        ],
    }


TEMPLATES = [{"id": "T1", "primary_muscle_group": "chest"}, {"id": "T2", "primary_muscle_group": "quadriceps"}]


def _df(weights):
    workouts = [_workout(day, w, 8) for day, w in zip(range(1, 29, 3), weights)]
    workouts.append(_workout(2, 100, 8, exercise="Sentadilla", template="T2"))
    return workouts_to_sets_df(workouts, TEMPLATES)


def test_series_por_musculo_y_estado():
    summary = build_training_summary(_df([80] * 6), weeks=4)
    muscles = {m["musculo"]: m for m in summary["series_por_musculo"]}

    # 6 sesiones x 3 series de pecho en 4 semanas = 4.5 series/semana
    assert muscles["chest"]["series_por_semana"] == 4.5
    assert muscles["chest"]["estado"] == "bajo"
    assert "quadriceps" in muscles


def test_tendencia_progresando_y_ultima_serie_real():
    summary = build_training_summary(_df([70, 72, 74, 76, 78, 80]), weeks=4)
    trend = summary["tendencias_ejercicios"][0]

    assert trend["ejercicio"] == "Press Banca"
    assert trend["estado"] == "progresando"
    # La última serie es el peso real, no el 1RM estimado
    assert trend["ultima_serie"] == {"peso_kg": 80.0, "reps": 8}
    assert trend["final"] > 80


def test_tendencia_estancada():
    summary = build_training_summary(_df([80] * 6), weeks=4)

    assert summary["tendencias_ejercicios"][0]["estado"] == "estancado"


def test_ejercicio_con_pocas_sesiones_no_tiene_tendencia():
    summary = build_training_summary(_df([80] * 6), weeks=4)

    assert "Sentadilla" not in [t["ejercicio"] for t in summary["tendencias_ejercicios"]]
