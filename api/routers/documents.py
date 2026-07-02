from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from api.dependencies import verify_api_key
from api.schemas import ConversorResponse
from api.services.document_service import DocumentService
from api.settings import get_settings

router = APIRouter(prefix="/v1/documents", tags=["documents"], dependencies=[Depends(verify_api_key)])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}

def get_document_service() -> DocumentService:
    return DocumentService()

@router.post("/convert", response_model=ConversorResponse)
async def convert_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
):
    file_name = file.filename or "unknow"
    extension = "." + file_name.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unssuported file type '{extension}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    
    file_bytes = await file.read()
    max_bytes = get_settings().max_file_size_mb * 1024 * 1024

    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
            detail=f"File exceeds {get_settings().max_file_size_mb} MB limit."
        )
    
    markdown = service.convert_to_markdown(file_bytes, file_name)
    return ConversorResponse(
        file_name=file_name,
        markdown=markdown,
        markkdown_length=len(markdown)
    )