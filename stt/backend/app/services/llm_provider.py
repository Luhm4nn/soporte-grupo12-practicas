import logging
from abc import ABC, abstractmethod

from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set. AI features will use mock responses.")
            self._available = False
            return
        try:
            from google import genai
            self._client = genai.Client(api_key=settings.gemini_api_key)
            self._available = True
        except Exception as e:
            logger.warning("Failed to initialize Gemini client: %s. Using mock.", e)
            self._available = False

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self._available:
            return self._mock_response(system_prompt, user_prompt)
        try:
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{system_prompt}\n\n{user_prompt}",
            )
            return response.text
        except Exception as e:
            logger.error("Gemini API error: %s", e)
            return self._mock_response(system_prompt, user_prompt)

    def _mock_response(self, system_prompt: str, user_prompt: str) -> str:
        if "improve" in system_prompt.lower():
            return user_prompt
        if "fillers" in system_prompt.lower():
            return user_prompt
        if "summary" in system_prompt.lower():
            return "Resumen del audio: " + user_prompt[:100] + "..."
        if "tasks" in system_prompt.lower():
            return '- [] Tarea 1 (sin fecha)\n- [] Tarea 2 (sin fecha)'
        if "dates" in system_prompt.lower():
            return "- mañana\n- viernes"
        if "phones" in system_prompt.lower():
            return "+54 11 1234 5678"
        if "emails" in system_prompt.lower():
            return "correo@ejemplo.com"
        if "links" in system_prompt.lower():
            return "https://ejemplo.com"
        if "tags" in system_prompt.lower():
            return "Trabajo, Reunión"
        if "chat" in system_prompt.lower():
            return "Basado en el audio, la respuesta a tu pregunta es..."
        return user_prompt


class MockProvider(BaseLLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return user_prompt


def get_llm_provider() -> BaseLLMProvider:
    provider_name = settings.llm_provider.lower()
    if provider_name == "gemini":
        return GeminiProvider()
    logger.warning("Unknown LLM provider '%s', using mock", provider_name)
    return MockProvider()
