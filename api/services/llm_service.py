from google import genai
from google.genai import errors, types

from api.settings import Settings


class LLMError(Exception):
    """Raised when the LLM provider fails to generate a response."""


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def summarize(self, markdown: str, max_words: int = 120) -> str:
        system_instruction = (
            "You are a summarization engine. "
            f"Summarize the following document in at most {max_words} words. "
            "Return only the summary, with no preamble."
        )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=markdown,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )
        except errors.APIError as error:
            raise LLMError(f"Gemini request failed: {error}") from error

        if not response.text:
            raise LLMError("Gemini returned an empty response.")

        return response.text.strip()