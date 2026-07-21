import io

from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter


class DocumentService:
    def __init__(self) -> None:
        self._converter = DocumentConverter()

    def convert_to_markdown(self, file_bytes: bytes, file_name: str) -> str:
        document_stream = DocumentStream(
            name=file_name,
            stream=io.BytesIO(file_bytes),
        )

        result = self._converter.convert(document_stream)
        return result.document.export_to_markdown()