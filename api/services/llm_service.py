from dataclasses import dataclass

from google import genai
from google.genai import errors, types

from api.settings import Settings


class LLMError(Exception):
    """Raised when the LLM provider fails to generate a response."""

@dataclass
class LLMResult:
    text: str
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def summarize(self, markdown: str, max_words: int = 120) -> LLMResult:
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

        return LLMResult(
            text=response.text,
            prompt_tokens=response.usage_metadata.prompt_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
            total_tokens=response.usage_metadata.total_token_count,
        )
    
    def ask(self, markdown: str, question: str) -> LLMResult:
        system_instruction = (
            "You are a document-based assistant. "
            "Answer the user's question using only the provided document. "
            "Do not invent, assume, or recreate information that is not present in the document. "
            "If the answer is not available in the document, say that the document does not contain enough information."
        )

        prompt = (
            f"Document: {markdown}"
            f"Question: {question}"
            "Answer:"
        )
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )
        except errors.APIError as error:
            raise LLMError(f"Gemini request failed: {error}") from error

        if not response.text:
            raise LLMError("Gemini returned an empty response.")

        return LLMResult(
            text=response.text,
            prompt_tokens=response.usage_metadata.prompt_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
            total_tokens=response.usage_metadata.total_token_count,
        )