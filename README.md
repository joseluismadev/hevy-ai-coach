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

## Datos de Hevy

Hevy Pro ofrece una API pública (https://api.hevyapp.com/docs). La clave se obtiene en
Ajustes > Developer y se envía en la cabecera `api-key`. El proyecto descarga:

- Tus entrenamientos (`/v1/workouts`) → `data/hevy_workouts.json`
- El catálogo de ejercicios (`/v1/exercise_templates`), que aporta el grupo muscular

Ambos ficheros son datos personales y están en `.gitignore`.

## Cómo arrancar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # rellena HEVY_API_KEY y LLM_API_KEY

python -m src.download_workouts # descarga tus datos de Hevy
python -m pytest                # tests
python -m src.evaluate          # evalúa el coach de IA contra tus datos
python -m src.app               # API en http://localhost:8000/docs
```

## Arquitectura del coach

```
Hevy API → dataset.py (1 fila por serie) → metrics.py (resumen) → coach.py (LLM) → /coach
                                                                       ↑
                                                         evaluate.py (comprobaciones)
```

- **El código calcula, el LLM interpreta.** El LLM nunca ve las miles de series en bruto,
  solo un resumen de métricas ya calculadas (series por músculo, tendencias de 1RM...).
- **Salida estructurada.** El informe sigue un esquema Pydantic (`CoachReport`), así que
  se puede validar y mostrar en una interfaz.
- **Independiente del proveedor.** Cualquier LLM compatible con la API de OpenAI (Gemini,
  Groq, OpenAI...) se configura con `LLM_API_KEY`, `LLM_BASE_URL` y `LLM_MODEL`.
- **Evaluación.** Cada error encontrado en las respuestas se convierte en una comprobación
  automática en `evaluate.py`.

## Objetivo del MVP

El primer objetivo no es construir una app gigante. Es construir algo funcional que te permita responder preguntas como:

- ¿Cuánto volumen llevo esta semana?
- ¿Qué músculos tengo más desarrollados?
- ¿Estoy progresando o estancado?
- ¿Qué debería entrenar la próxima semana?

## Estado

- [x] Descarga de entrenamientos reales desde la API de Hevy
- [x] Dataset con una fila por serie, 1RM estimado y grupo muscular
- [x] Notebook de exploración (`notebooks/01_exploracion.ipynb`)
- [x] Coach de IA con salida estructurada y endpoint `/coach`
- [x] Evaluación automática del coach (`python -m src.evaluate`)
- [ ] Comparar varios modelos con la misma evaluación
- [ ] Dashboard simple

## Nota

Este proyecto está pensado como un camino de aprendizaje práctico. No necesitas llegar a un producto final desde el principio; lo importante es construir, probar y mejorar de forma iterativa.
