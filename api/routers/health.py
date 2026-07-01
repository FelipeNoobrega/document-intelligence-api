from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["health"])

@router.get("/health")
def health_check() -> dict:
    return {"status":"ok", "service":"document-intelligence-api"}