from pydantic import BaseModel

class ConvertResponse(BaseModel):
    file_name: str
    markdown: str
    markdown_length: int


class SummarizeResponse(BaseModel):
    file_name: str
    summary: str
    summary_length: int
    original_markdown_length: int


class AskResponse(BaseModel):
    file_name: str
    question: str
    answer: str
    original_markdown_length: int
    question_length: int