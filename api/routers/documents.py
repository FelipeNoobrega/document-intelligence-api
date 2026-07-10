from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Query

from api.dependencies import verify_api_key
from api.schemas import AskResponse, ConvertResponse, SummarizeResponse
from api.services.document_service import DocumentService
from api.services.llm_service import LLMService, LLMError
from api.settings import get_settings


router = APIRouter(prefix="/v1/documents", tags=["documents"], dependencies=[Depends(verify_api_key)])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}


def get_document_service() -> DocumentService:
    return DocumentService()

def get_llm_service() -> LLMService:
    return LLMService(get_settings())


@router.post("/convert", response_model=ConvertResponse)
async def convert_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
):
    file_name = file.filename or "unknown"
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsuported file type '{extension}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    
    file_bytes = await file.read()
    max_bytes = get_settings().max_file_size_mb * 1024 * 1024

    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {get_settings().max_file_size_mb} MB limit."
        )
    
    markdown = service.convert_to_markdown(file_bytes, file_name)
    return ConvertResponse(
        file_name=file_name,
        markdown=markdown,
        markdown_length=len(markdown)
    )

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(
    file: UploadFile = File(...),
    max_words: int = Query(default=150, ge=10, le=1000),
    doc_service: DocumentService = Depends(get_document_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    file_name = file.filename or "unknown"
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsuported file type '{extension}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    
    file_bytes = await file.read()
    max_bytes = get_settings().max_file_size_mb * 1024 * 1024

    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {get_settings().max_file_size_mb} MB limit."
        )
    
    markdown = doc_service.convert_to_markdown(file_bytes, file_name)

    try: 
        summary = llm_service.summarize(markdown, max_words)
    except LLMError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )
    
    return SummarizeResponse(
        file_name=file_name,
        summary=summary.text,
        summary_length=len(summary.text),
        original_markdown_length=len(markdown),
        prompt_tokens=summary.prompt_tokens,
        output_tokens=summary.output_tokens,
        total_tokens=summary.total_tokens,
        
    )

@router.post("/ask", response_model=AskResponse)
async def ask_document(
    file: UploadFile = File(...),
    question: str = Form(..., min_length=1),
    doc_service: DocumentService = Depends(get_document_service),
    llm_service: LLMService = Depends(get_llm_service),

):
    file_name = file.filename or "unknown"
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsuported file type '{extension}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    
    file_bytes = await file.read()
    max_bytes = get_settings().max_file_size_mb * 1024 * 1024

    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {get_settings().max_file_size_mb} MB limit."
        )
    
    markdown = doc_service.convert_to_markdown(file_bytes, file_name)

    try: 
        answer = llm_service.ask(markdown, question)
    except LLMError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )
    
    return AskResponse(
        file_name=file_name,
        question=question,
        answer=answer.text,
        original_markdown_length=len(markdown),
        question_length=len(question),
        prompt_tokens=answer.prompt_tokens,
        output_tokens=answer.output_tokens,
        total_tokens=answer.total_tokens,
    )