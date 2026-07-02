from pydantic import BaseModel

class ConversorResponse(BaseModel):
    file_name: str
    markdown: str
    markkdown_length: int


class SummarizeResponse(BaseModel):
    file_name: str
    summary: str
    summary_length: int
    original_markdown_length: int