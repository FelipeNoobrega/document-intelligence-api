import tempfile
import os

from google import genai
from google.genai import errors


from api.settings import Settings



class TokenServiceError(Exception):
    """Raised when token counting from the Gemini File API fails."""


class TokenService:
    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def count_pdf_native_tokens(self, file_bytes: bytes) -> int:
        tmp_path = None
        remote_file = None  

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            remote_file = self._client.files.upload(file=tmp_path)

            result = self._client.models.count_tokens(
                model=self._model,
                contents=[remote_file],
            )
            return result.total_tokens
        

        except errors.APIError as error:
            raise TokenServiceError(
                f"File API token counting failed: {error}"
            ) from error
        

        finally:
            if remote_file is not None:
                self._client.files.delete(name=remote_file.name)

            if tmp_path is not None:
                os.remove(tmp_path)

    
    def count_markdown_tokens(self, markdown: str) -> int:
        try:
            result = self._client.models.count_tokens(
                model=self._model,
                contents=markdown,
            )
            return result.total_tokens
        
        
        except errors.APIError as error:
            raise TokenServiceError(
                f"Markdown token counting failed: {error}"
            ) from error
        