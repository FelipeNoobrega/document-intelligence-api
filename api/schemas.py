from pydantic import BaseModel, computed_field


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


class CountTokensResponse(FileResponse):
    total_pdf_token: int
    total_markdown_token: int
    model:str
    
    @computed_field
    @property
    def token_change_percent(self) -> float:
        if self.total_pdf_token == 0:
            return 0.0
        return round(((self.total_markdown_token - self.total_pdf_token) / self.total_pdf_token)  * 100, 2)
   