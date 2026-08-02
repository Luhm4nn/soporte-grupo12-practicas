import logging
import json

from app.services.llm_provider import get_llm_provider, BaseLLMProvider

logger = logging.getLogger(__name__)

PROMPTS = {
    "improve": (
        "Eres un asistente que mejora la redacción de transcripciones de audio manteniendo el significado original. "
        "Corrige errores gramaticales, mejora la claridad y estructura, pero no cambies el contenido ni agregues información nueva. "
        "Responde SOLO con el texto mejorado, sin introducciones ni explicaciones."
    ),
    "remove_fillers": (
        "Eres un asistente que elimina muletillas de transcripciones de audio. "
        "Elimina palabras como: eee, emm, viste, o sea, tipo, bueno, nada, digamos, este, eh, ah, mm. "
        "No cambies el significado ni la estructura general. "
        "Responde SOLO con el texto limpio, sin introducciones ni explicaciones."
    ),
    "summarize_short": (
        "Eres un asistente que resume transcripciones de audio. "
        "Genera un resumen CORTO (1-2 oraciones) con lo más importante. "
        "Responde SOLO con el resumen."
    ),
    "summarize_medium": (
        "Eres un asistente que resume transcripciones de audio. "
        "Genera un resumen MEDIO (1 párrafo) capturando los puntos clave. "
        "Responde SOLO con el resumen."
    ),
    "summarize_detailed": (
        "Eres un asistente que resume transcripciones de audio. "
        "Genera un resumen DETALLADO (3-4 párrafos) cubriendo todos los temas importantes. "
        "Responde SOLO con el resumen."
    ),
    "tasks": (
        "Eres un asistente que extrae tareas y acciones de transcripciones de audio. "
        "Identifica todas las tareas, acciones o pendientes mencionados. "
        "Para cada tarea, detecta si hay una fecha límite o responsable. "
        "Responde SOLO con una lista JSON donde cada elemento tiene: {\"task\": string, \"deadline\": string | null, \"responsible\": string | null}. "
        "Ejemplo: [{\"task\": \"Hacer flyer\", \"deadline\": \"viernes\", \"responsible\": null}]"
    ),
    "dates": (
        "Eres un asistente que extrae todas las referencias temporales y fechas de transcripciones de audio. "
        "Busca: días de la semana, fechas, horas, palabras como mañana, pasado mañana, etc. "
        "Responde SOLO con una lista JSON de strings. Ejemplo: [\"mañana\", \"viernes\", \"14:30\"]"
    ),
    "phones": (
        "Eres un asistente que extrae números de teléfono de transcripciones de audio. "
        "Incluye teléfonos nacionales e internacionales. "
        "Responde SOLO con una lista JSON de strings. Ejemplo: [\"+54 11 1234 5678\"]"
    ),
    "emails": (
        "Eres un asistente que extrae direcciones de email de transcripciones de audio. "
        "Responde SOLO con una lista JSON de strings. Ejemplo: [\"usuario@ejemplo.com\"]"
    ),
    "links": (
        "Eres un asistente que extrae enlaces y URLs de transcripciones de audio. "
        "Incluye URLs completas, dominios y enlaces abreviados. "
        "Responde SOLO con una lista JSON de strings. Ejemplo: [\"https://ejemplo.com\"]"
    ),
    "tags": (
        "Eres un asistente que clasifica transcripciones de audio en categorías. "
        "Elige las categorías más apropiadas de esta lista: Trabajo, Facultad, Personal, Cliente, Ventas, Compras, Urgente, Recordatorio, Reunión, Ideas. "
        "Responde SOLO con una lista JSON de strings. Ejemplo: [\"Trabajo\", \"Reunión\"]"
    ),
}


def _call_llm(provider: BaseLLMProvider, system_prompt: str, text: str) -> str:
    return provider.generate(system_prompt, text)


def improve_text(text: str) -> str:
    provider = get_llm_provider()
    return _call_llm(provider, PROMPTS["improve"], text)


def remove_fillers(text: str) -> str:
    provider = get_llm_provider()
    return _call_llm(provider, PROMPTS["remove_fillers"], text)


def summarize(text: str, level: str = "medium") -> str:
    provider = get_llm_provider()
    key = f"summarize_{level}"
    prompt = PROMPTS.get(key, PROMPTS["summarize_medium"])
    return _call_llm(provider, prompt, text)


def extract_tasks(text: str) -> list[dict]:
    provider = get_llm_provider()
    result = _call_llm(provider, PROMPTS["tasks"], text)
    return _parse_json_list(result)


def extract_dates(text: str) -> list[str]:
    provider = get_llm_provider()
    result = _call_llm(provider, PROMPTS["dates"], text)
    return _parse_json_list(result)


def extract_phones(text: str) -> list[str]:
    provider = get_llm_provider()
    result = _call_llm(provider, PROMPTS["phones"], text)
    return _parse_json_list(result)


def extract_emails(text: str) -> list[str]:
    provider = get_llm_provider()
    result = _call_llm(provider, PROMPTS["emails"], text)
    return _parse_json_list(result)


def extract_links(text: str) -> list[str]:
    provider = get_llm_provider()
    result = _call_llm(provider, PROMPTS["links"], text)
    return _parse_json_list(result)


def extract_tags(text: str) -> list[str]:
    provider = get_llm_provider()
    result = _call_llm(provider, PROMPTS["tags"], text)
    return _parse_json_list(result)


def chat_with_transcription(transcription: str, question: str) -> str:
    provider = get_llm_provider()
    system_prompt = (
        "Eres un asistente que responde preguntas sobre el contenido de un audio transcripto. "
        "Solo puedes usar la información proporcionada en la transcripción. "
        "Si la respuesta no está en el texto, indícalo amablemente. "
        "Responde en español de forma clara y concisa."
    )
    user_prompt = f"Transcripción del audio:\n{transcription}\n\nPregunta del usuario:\n{question}"
    return _call_llm(provider, system_prompt, user_prompt)


def _parse_json_list(result: str) -> list:
    result = result.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[-1]
        if result.endswith("```"):
            result = result.rsplit("```", 1)[0]
    result = result.strip()
    try:
        parsed = json.loads(result)
        if isinstance(parsed, list):
            return parsed
        return [str(parsed)]
    except json.JSONDecodeError:
        lines = [l.strip("- []* ") for l in result.split("\n") if l.strip()]
        return lines if lines else [result]
