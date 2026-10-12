from src.dataset import estimate_1rm, workouts_to_sets_df

WORKOUTS = [
    {
        "id": "w1",
        "title": "Empuje",
        "start_time": "2026-10-06T10:00:00+00:00",
        "end_time": "2026-10-06T11:00:00+00:00",
        "exercises": [
            {
                "title": "Press Banca",
                "exercise_template_id": "T1",
                "sets": [
                    {"index": 0, "type": "warmup", "weight_kg": 40, "reps": 10},
                    {"index": 1, "type": "normal", "weight_kg": 80, "reps": 8},
                    {"index": 2, "type": "normal", "weight_kg": 80, "reps": 6},
                ],
            },
            {
                "title": "Fondos",
                "exercise_template_id": "T2",
                "sets": [{"index": 0, "type": "normal", "weight_kg": None, "reps": 12}],
            },
        ],
    }
]

TEMPLATES = [{"id": "T1", "primary_muscle_group": "chest"}]


def test_estimate_1rm():
    assert estimate_1rm(100, 1) == 100
    assert estimate_1rm(90, 10) == 120
    assert estimate_1rm(0, 10) == 0
    assert estimate_1rm(None, 5) == 0


def test_workouts_to_sets_df_una_fila_por_serie():
    df = workouts_to_sets_df(WORKOUTS, TEMPLATES)

    assert len(df) == 4
    assert df["is_warmup"].sum() == 1
    assert df.loc[df["exercise"] == "Press Banca", "volume_kg"].tolist() == [400, 640, 480]


def test_workouts_to_sets_df_grupo_muscular():
    df = workouts_to_sets_df(WORKOUTS, TEMPLATES)
    muscles = df.groupby("exercise")["muscle_group"].first().to_dict()

    assert muscles == {"Press Banca": "chest", "Fondos": "unknown"}


def test_workouts_to_sets_df_peso_corporal_sin_volumen():
    df = workouts_to_sets_df(WORKOUTS, TEMPLATES)
    fondos = df[df["exercise"] == "Fondos"].iloc[0]

    assert fondos["volume_kg"] == 0
    assert fondos["reps"] == 12


def test_workouts_to_sets_df_vacio():
    assert workouts_to_sets_df([]).empty


def test_workouts_to_sets_df_semana_empieza_en_lunes():
    df = workouts_to_sets_df(WORKOUTS, TEMPLATES)

    # 2026-10-06 es martes -> su semana empieza el lunes 2026-10-05
    assert str(df["week"].iloc[0]) == "2026-10-05"
