from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.dependencies import verify_api_key
from api.main import app
from api.routers.documents import get_document_service, get_llm_service
from api.services.llm_service import LLMError


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



def test_summarize_returns_200_and_summary():
    fake_doc = MagicMock()
    fake_doc.convert_to_markdown.return_value = "# Title\n\nContent test fake markdown"
    fake_llm = MagicMock()
    fake_llm.summarize.return_value = "A short summary."

    app.dependency_overrides[get_document_service] = lambda: fake_doc
    app.dependency_overrides[get_llm_service] = lambda: fake_llm
    app.dependency_overrides[verify_api_key] = lambda: None

    client = TestClient(app)
    files = {"file": ("document.pdf", b"fake bytes", "application/pdf")}
    response = client.post("/v1/documents/summarize?max_words=50", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "A short summary."
    assert body["file_name"] == "document.pdf"
    app.dependency_overrides.clear()



def test_summarize_returns_502_when_llm_fails():
    fake_doc = MagicMock()
    fake_doc.convert_to_markdown.return_value = "# Title"
    fake_llm  = MagicMock()
    fake_llm.summarize.side_effect = LLMError("Gemini request failed")

    app.dependency_overrides[get_document_service] = lambda: fake_doc
    app.dependency_overrides[get_llm_service] = lambda: fake_llm
    app.dependency_overrides[verify_api_key] = lambda: None

    client = TestClient(app) 
    files = {"file": ("report.pdf", b"fake", "application/pdf")}
    response = client.post("/v1/documents/summarize", files=files)

    assert response.status_code == 502
    app.dependency_overrides.clear()



def test_ask_returns_200_and_answer():
    fake_doc = MagicMock()
    fake_doc.convert_to_markdown.return_value = "# Title\n\nContent test fake markdown"

    fake_quest = "what is the title?"

    fake_llm = MagicMock()
    fake_llm.ask.return_value = "answer for the document."

    app.dependency_overrides[get_document_service] = lambda: fake_doc
    app.dependency_overrides[get_llm_service] = lambda: fake_llm
    app.dependency_overrides[verify_api_key] = lambda: None

    client = TestClient(app)
    files = {"file": ("document.pdf", b"fake", "application/pdf")}

    try:
        response = client.post(
        "/v1/documents/ask", 
        files=files, 
        data={"question": fake_quest}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["file_name"] == "document.pdf"
        assert body["question"] == fake_quest
        assert body["original_markdown_length"] == len("# Title\n\nContent test fake markdown")
        assert body["question_length"] == len(fake_quest)

        fake_doc.convert_to_markdown.assert_called_once_with(
                b"fake",
                "document.pdf",
            )

        fake_llm.ask.assert_called_once_with(
            "# Title\n\nContent test fake markdown",
            fake_quest,
        )

    finally:
        app.dependency_overrides.clear()



def test_ask_returns_502_when_llm_fails():
    fake_doc = MagicMock()
    fake_doc.convert_to_markdown.return_value = "# Title\n\nContent test fake markdown"

    fake_quest = "what is the title?"

    fake_llm  = MagicMock()
    fake_llm.ask.side_effect = LLMError("Gemini request failed")

    app.dependency_overrides[get_document_service] = lambda: fake_doc
    app.dependency_overrides[get_llm_service] = lambda: fake_llm
    app.dependency_overrides[verify_api_key] = lambda: None

    client = TestClient(app) 
    files = {"file": ("report.pdf", b"fake", "application/pdf")}
    try:
        response = client.post(
            "/v1/documents/ask", 
            files=files,
            data={"question": fake_quest}
        )

        assert response.status_code == 502
        
    finally:
        app.dependency_overrides.clear()


