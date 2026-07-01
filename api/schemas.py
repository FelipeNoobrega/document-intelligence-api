from pydantic import BaseModel

class ConversorResponse(BaseModel):
    file_name: str
    markdown: str
    markkdown_length: int