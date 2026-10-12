from types import SimpleNamespace

from src.coach import Accion, CoachReport, Problema, build_messages, generate_coach_report
from src.evaluate import detecta_tren_inferior, evidencia_verificable, no_usa_1rm_como_peso

SUMMARY = {
    "periodo": {"desde": "2026-08-15", "hasta": "2026-10-10", "semanas": 8},
    "series_por_musculo": [{"musculo": "quadriceps", "series_por_semana": 6.2, "estado": "bajo"}],
    "tendencias_ejercicios": [
        {
            "ejercicio": "Elevación Lateral (Máquina)",
            "final": 11.6,
            "ultima_serie": {"peso_kg": 8.5, "reps": 10},
        }
    ],
}


def _report(evidencia="Cuádriceps a 6.2 series por semana", accion="Elevación lateral con 8.5 kg"):
    return CoachReport(
        resumen="Buen trabajo",
        puntos_fuertes=["Constancia"],
        problemas=[Problema(titulo="Poco volumen de pierna", evidencia=evidencia, prioridad="alta")],
        plan_proxima_semana=[Accion(accion=accion, motivo="Progresar")],
    )


class FakeClient:
    """Imita al cliente de OpenAI para probar sin llamar al LLM."""

    def __init__(self, report):
        self.calls = []
        parse = lambda **kwargs: self.calls.append(kwargs) or SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(parsed=report))]
        )
        self.chat = SimpleNamespace(completions=SimpleNamespace(parse=parse))


def test_build_messages_incluye_el_resumen():
    messages = build_messages(SUMMARY)

    assert messages[0]["role"] == "system"
    assert "Elevación Lateral (Máquina)" in messages[1]["content"]
    assert "8 semanas" in messages[1]["content"]


def test_generate_coach_report_pide_salida_estructurada():
    client = FakeClient(_report())

    report = generate_coach_report(SUMMARY, client=client, model="modelo-test")

    assert report.problemas[0].prioridad == "alta"
    assert client.calls[0]["response_format"] is CoachReport
    assert client.calls[0]["model"] == "modelo-test"


# --- Tests del evaluador: comprobamos que detecta los informes malos ---


def test_evaluador_detecta_1rm_usado_como_peso():
    ok, detail = no_usa_1rm_como_peso(_report(accion="Sube la elevación lateral a 11.6 kg"), SUMMARY)

    assert not ok
    assert "11.6" in detail


def test_evaluador_acepta_peso_real():
    ok, _ = no_usa_1rm_como_peso(_report(), SUMMARY)

    assert ok


def test_evaluador_detecta_cifras_inventadas():
    ok, _ = evidencia_verificable(_report(evidencia="Cuádriceps a 3.1 series y 42 sesiones"), SUMMARY)

    assert not ok


def test_evaluador_detecta_que_falta_el_tren_inferior():
    report = _report()
    report.problemas[0].titulo = "Poco volumen de hombro"
    report.problemas[0].evidencia = "Hombros a 6.2 series"

    ok, _ = detecta_tren_inferior(report, SUMMARY)

    assert not ok
