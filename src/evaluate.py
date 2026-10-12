"""Evaluación del coach de IA contra tus datos reales.

Un LLM no es determinista: la misma pregunta puede dar respuestas distintas.
Por eso se ejecuta varias veces y se mide qué porcentaje de veces pasa cada comprobación.

Uso:
    python -m src.evaluate            # 3 ejecuciones
    python -m src.evaluate --runs 5
"""

import argparse
import json
import re
from typing import Any, Callable, Dict, List, Set, Tuple

from .coach import CoachReport, generate_coach_report
from .config import LLM_MODEL
from .dataset import load_sets_df
from .metrics import build_training_summary

LOWER_BODY_WORDS = ("pierna", "tren inferior", "cuádriceps", "cuadriceps", "isquio", "femoral", "glúteo", "gluteo")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")
# Mínimo de cifras de la evidencia que deben aparecer tal cual en el resumen
MIN_GROUNDED_RATIO = 0.8


def _normalize(number: str) -> str:
    value = float(number.replace(",", "."))
    return str(int(value)) if value.is_integer() else str(round(value, 1))


def _summary_numbers(summary: Dict[str, Any]) -> Set[str]:
    return {_normalize(n) for n in NUMBER_RE.findall(json.dumps(summary))}


def detecta_tren_inferior(report: CoachReport, summary: Dict[str, Any]) -> Tuple[bool, str]:
    """Con tus datos actuales, el bajo volumen de piernas es el problema más claro."""
    text = " ".join(f"{p.titulo} {p.evidencia}" for p in report.problemas).lower()
    found = any(word in text for word in LOWER_BODY_WORDS)
    return found, "menciona el tren inferior" if found else "no detecta el bajo volumen de piernas"


def evidencia_verificable(report: CoachReport, summary: Dict[str, Any]) -> Tuple[bool, str]:
    """Las cifras citadas como evidencia deben salir del resumen (detecta números inventados)."""
    known = _summary_numbers(summary)
    cited = [_normalize(n) for p in report.problemas for n in NUMBER_RE.findall(p.evidencia)]
    if not cited:
        return False, "la evidencia no cita ninguna cifra"
    missing = [n for n in cited if n not in known]
    ratio = 1 - len(missing) / len(cited)
    return ratio >= MIN_GROUNDED_RATIO, f"{ratio:.0%} de cifras verificables; no encontradas: {missing[:5]}"


def plan_acotado(report: CoachReport, summary: Dict[str, Any]) -> Tuple[bool, str]:
    n = len(report.plan_proxima_semana)
    return 1 <= n <= 5, f"{n} acciones"


def no_usa_1rm_como_peso(report: CoachReport, summary: Dict[str, Any]) -> Tuple[bool, str]:
    """Regresión del primer error encontrado: recomendar el 1RM estimado como peso de trabajo."""
    e1rm_values = set()
    real_weights = set()
    for trend in summary["tendencias_ejercicios"]:
        if trend["ultima_serie"]["peso_kg"] is not None:
            e1rm_values.add(_normalize(str(trend["final"])))
            real_weights.add(_normalize(str(trend["ultima_serie"]["peso_kg"])))

    plan_text = " ".join(a.accion for a in report.plan_proxima_semana)
    weights_in_plan = {_normalize(n) for n in re.findall(r"(\d+(?:[.,]\d+)?)\s*kg", plan_text)}
    suspicious = sorted((weights_in_plan & e1rm_values) - real_weights)
    return not suspicious, f"pesos sospechosos: {suspicious}" if suspicious else "ok"


CHECKS: List[Callable[[CoachReport, Dict[str, Any]], Tuple[bool, str]]] = [
    detecta_tren_inferior,
    evidencia_verificable,
    plan_acotado,
    no_usa_1rm_como_peso,
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evalúa el coach de IA")
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    summary = build_training_summary(load_sets_df())
    passed = {check.__name__: 0 for check in CHECKS}

    print(f"Modelo: {LLM_MODEL} | ejecuciones: {args.runs}\n")
    for run in range(1, args.runs + 1):
        report = generate_coach_report(summary)
        print(f"Ejecución {run}")
        for check in CHECKS:
            ok, detail = check(report, summary)
            passed[check.__name__] += ok
            print(f"  {'✅' if ok else '❌'} {check.__name__}: {detail}")
        print()

    print("Resultado")
    for name, count in passed.items():
        print(f"  {name}: {count}/{args.runs} ({count / args.runs:.0%})")


if __name__ == "__main__":
    main()
