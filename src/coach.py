"""Coach de entrenamiento con un LLM.

Recibe el resumen de `metrics.build_training_summary` y devuelve un informe con
estructura fija (salida estructurada), validado con Pydantic.
"""

import json
from typing import Any, Dict, List, Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

SYSTEM_PROMPT = """Eres un entrenador personal experto en hipertrofia y fuerza.
Analizas el resumen de entrenamiento de tu cliente y le das un informe claro y accionable.

Reglas:
- Basa cada afirmación en los datos del resumen y cita las cifras concretas como evidencia.
- No inventes datos que no estén en el resumen. Si falta información para afirmar algo, dilo.
- Usa como referencia orientativa 10-20 series efectivas por músculo y semana. Los músculos
  pequeños (abdominales, gemelos, trapecios, antebrazos) pueden necesitar menos trabajo directo.
- Ten en cuenta la nota del resumen sobre el trabajo indirecto de los músculos secundarios.
- El 1RM estimado sirve para medir la tendencia, NO es un peso de entrenamiento. Para recomendar
  cargas, parte de `ultima_serie` (peso y repeticiones reales de la última sesión).
- Da como máximo 5 acciones para la próxima semana, concretas (ejercicio, series, repeticiones).
- Prioriza: los problemas de prioridad alta son los que más limitan el progreso.
- No das consejo médico. Si algo sugiere lesión o dolor, recomienda consultar a un profesional.
- Responde en español, con un tono directo y cercano."""


class Problema(BaseModel):
    titulo: str
    evidencia: str = Field(description="Cifras del resumen que demuestran el problema")
    prioridad: Literal["alta", "media", "baja"]


class Accion(BaseModel):
    accion: str = Field(description="Qué hacer, con ejercicio, series y repeticiones si aplica")
    motivo: str


class CoachReport(BaseModel):
    resumen: str = Field(description="Diagnóstico general en 2-3 frases")
    puntos_fuertes: List[str]
    problemas: List[Problema]
    plan_proxima_semana: List[Accion]


def get_client() -> OpenAI:
    if not LLM_API_KEY:
        raise RuntimeError("Falta LLM_API_KEY. Añádela a tu archivo .env")
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def build_messages(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    summary_json = json.dumps(summary, ensure_ascii=False, indent=2)
    user_prompt = (
        f"Este es el resumen de mis últimas {summary['periodo']['semanas']} semanas de entrenamiento:\n\n"
        f"```json\n{summary_json}\n```\n\n"
        "Analiza mi entrenamiento y dime qué debo cambiar."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def generate_coach_report(
    summary: Dict[str, Any], client: Optional[OpenAI] = None, model: str = LLM_MODEL
) -> CoachReport:
    """Pide el informe al LLM forzando que la respuesta siga el esquema de CoachReport."""
    client = client or get_client()
    completion = client.chat.completions.parse(
        model=model,
        messages=build_messages(summary),
        response_format=CoachReport,
    )
    report = completion.choices[0].message.parsed
    if report is None:
        raise RuntimeError("El modelo no devolvió un informe válido")
    return report
