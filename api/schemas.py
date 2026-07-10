from pydantic import BaseModel


class FileResponse(BaseModel):
    file_name: str


class UsageToken(BaseModel):
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


class ConvertResponse(FileResponse): 
    markdown: str
    markdown_length: int


class SummarizeResponse(FileResponse, UsageToken):
    summary: str
    summary_length: int
    original_markdown_length: int
    

class AskResponse(FileResponse, UsageToken):
    question: str
    answer: str
    original_markdown_length: int
    question_length: int
   