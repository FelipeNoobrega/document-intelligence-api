from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.main import app
from api.routers.documents import get_document_service
from api.dependencies import verify_api_key


def test_convert_returns_200_and_markdown():
    fake_service = MagicMock()
    fake_service.convert_to_markdown.return_value = "# Title\n\nContent test fake markdown"
    app.dependency_overrides[get_document_service] = lambda: fake_service
    app.dependency_overrides[verify_api_key] = lambda: None

    client = TestClient(app)
    files = {"file": ("document.pdf", b"fake bytes", "application/pdf")}
    response = client.post("/v1/documents/convert", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["markdown"] == "# Title\n\nContent test fake markdown"
    assert body["file_name"] == "document.pdf"
    app.dependency_overrides.clear()



def test_convert_rejects_unsupported_extension():
    app.dependency_overrides[verify_api_key] = lambda: None
    client = TestClient(app)
    files = {"file": ("notes.txt", b"fake bytes", "text/plain")}
    response = client.post("/v1/documents/convert", files=files)

    assert response.status_code == 400
    app.dependency_overrides.clear()



def test_convert_requires_api_key():
    files = {"file": ("letter.pdf", b"fake bytes", "application/pdf")}
    client = TestClient(app)
    response = client.post("/v1/documents/convert", files=files)

    assert response.status_code == 401