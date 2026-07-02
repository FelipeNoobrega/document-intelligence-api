import io

from markitdown import MarkItDown

class DocumentService:
    def __init__(self) -> None:
        self._converter = MarkItDown()

    def convert_to_markdown(self, file_bytes: bytes, file_name: str) -> str:
        stream = io.BytesIO(file_bytes)
        stream.name = file_name

        result = self._converter.convert_stream(stream)
        return result.text_content