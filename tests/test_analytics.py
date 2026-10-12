from src.analytics import compute_session_volume, muscle_distribution, summarize_workouts


def test_compute_session_volume():
    session = {
        "workout_name": "Push day",
        "exercises": [
            {"name": "Bench Press", "sets": 5, "reps": 8, "weight_kg": 70},
            {"name": "Overhead Press", "sets": 4, "reps": 8, "weight_kg": 40},
        ],
    }

    assert compute_session_volume(session) == 4080.0


def test_summarize_workouts():
    workouts = [
        {
            "date": "2026-10-01",
            "workout_name": "Push day",
            "exercises": [{"sets": 3, "reps": 10, "weight_kg": 50}],
        }
    ]

    items = summarize_workouts(workouts)
    assert items[0]["workout_name"] == "Push day"
    assert items[0]["total_volume"] == 1500.0


def test_muscle_distribution():
    workouts = [
        {
            "exercises": [
                {"muscle_group": "Chest", "sets": 3, "reps": 8, "weight_kg": 60},
                {"muscle_group": "Back", "sets": 4, "reps": 8, "weight_kg": 50},
            ]
        }
    ]

    distribution = muscle_distribution(workouts)
    assert distribution["Back"] == 1600.0
    assert distribution["Chest"] == 1440.0
