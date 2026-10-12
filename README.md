# Hevy AI Coach

Este proyecto nace para aprender IA aplicada a fitness usando Hevy Pro como fuente de datos. La idea es construir poco a poco un asistente que lea tus entrenamientos, detecte patrones, y te ayude a mejorar tus progresos con recomendaciones automáticas.

## Objetivo

Crear un MVP con estas capacidades:

- Extraer o importar sesiones de entrenamiento desde Hevy.
- Procesar datos de volumen, frecuencia y progreso.
- Generar análisis útiles con Python y data science.
- Exponer una API simple para consultar insights.
- Usar IA para resumir entrenamiento y recomendar próximos pasos.

## Stack sugerido

- Python
- FastAPI
- Pandas
- OpenAI / modelos de lenguaje
- SQLite o JSON para almacenamiento local
- Docker opcional en etapas avanzadas

## Estructura del proyecto

- `src/`: lógica principal del proyecto.
- `data/`: archivos JSON de ejemplo para entrenamientos.
- `notebooks/`: cuadernos de exploración y aprendizaje.
- `tests/`: pruebas de validación.

## Roadmap de aprendizaje

### Etapa 1: datos y limpieza
- Entender el formato de tus entrenamientos.
- Guardar datos en JSON/CSV.
- Limpiar columnas, series temporales y ejercicios.

### Etapa 2: análisis de entrenamiento
- Calcular volumen por sesión.
- Revisar volumen por músculo.
- Detectar mejora o regresión en series y pesos.

### Etapa 3: IA aplicada
- Generar resúmenes con LLM.
- Crear prompts para recomendaciones de progreso.
- Evaluar si la respuesta del modelo es útil y accionable.

### Etapa 4: producto
- Crear una API con FastAPI.
- Añadir dashboard simple.
- Preparar despliegue local o en la nube.

## Recomendación realista para Hevy

Hevy Pro te da acceso a una mejor experiencia de seguimiento, pero no siempre existen endpoints públicos listos para consumir. Por eso, esta base de proyecto está pensada para trabajar en dos caminos:

1. Importación manual desde exportaciones o JSON.
2. Integración futura con una API o automatización si Hevy lo permite.

La idea es que el proyecto aprenda bien el flujo completo de IA: datos, análisis y generación de valor, sin depender del 100% de una API externa.

## Cómo arrancar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.app
```

## Objetivo del MVP

El primer objetivo no es construir una app gigante. Es construir algo funcional que te permita responder preguntas como:

- ¿Cuánto volumen llevo esta semana?
- ¿Qué músculos tengo más desarrollados?
- ¿Estoy progresando o estancado?
- ¿Qué debería entrenar la próxima semana?

## Siguiente paso sugerido

- Recolecta 3 a 10 entrenamientos reales en JSON.
- Organiza los ejercicios por músculo y peso.
- Crea funciones para calcular volumen y progreso.
- Añade un prompt para un coach de IA.

## Nota

Este proyecto está pensado como un camino de aprendizaje práctico. No necesitas llegar a un producto final desde el principio; lo importante es construir, probar y mejorar de forma iterativa.
