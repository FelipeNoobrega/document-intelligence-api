# Document Intelligence API

A FastAPI service that converts real-world documents (PDF, DOCX, PPTX, XLSX) into
clean, **LLM-ready Markdown** — reducing the token overhead of feeding raw
documents to a model, and improving answer quality before any AI model touches
the content.

This project sits at the **document ingestion layer**: the step *between* messy
source files and an LLM pipeline. Feeding raw PDFs to a language model is
expensive, because each page is often processed as an image, inflating token
usage. Converting to structured Markdown first strips that overhead while
preserving the document's structure (headings, lists, tables). Quantifying the
exact saving — a side-by-side comparison with and without the conversion step —
is part of the [Roadmap](#roadmap).

---

## Motivation

While working on a corporate chatbot in a previous role, I needed a language
model to answer questions over internal documents — policies, process
hierarchies, department interfaces, company history — all provided as PDFs.
Feeding those PDFs to the model consumed a large number of tokens per request.
One alternative was to store the documents as embeddings in a vector store, but
that introduced its own storage and query costs.

Now, building personal projects that also rely on LLMs, I kept running into the
same problem. This project is my attempt to address it using Microsoft's
open-source MarkItDown library: the first version receives documents in these
formats and converts them into Markdown, and later versions will forward the
result to an LLM. The goal is to improve the model's answers while reducing token
usage — which is why a future version includes a side-by-side token-cost
comparison, with and without the conversion step.

---

## Table of Contents

- [Motivation](#motivation)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the API](#running-the-api)
- [API Reference](#api-reference)
- [Scope and Limitations](#scope-and-limitations)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Tech Stack](#tech-stack)
- [References](#references)

---

## Features

**Available now (V1):**

- Convert `PDF`, `DOCX`, `PPTX`, and `XLSX` files into clean Markdown via a single
  endpoint — no format-specific logic on the client side.
- API key authentication on protected routes.
- Input validation at the boundary: file-type allowlist and configurable
  maximum file size.
- Health check endpoint for monitoring and deployment probes.
- Automated tests covering the happy path, rejected file types, and auth.

**Planned (see [Roadmap](#roadmap)):** token-cost estimation, LLM-powered
summarization, question answering over documents, and structured field
extraction.

---

## Architecture

The service follows a clean separation of responsibilities so that business
logic never lives inside HTTP handlers:

```
Client → Router (HTTP boundary) → Service (business logic) → MarkItDown
             │                          │
       validates input           converts document
       checks auth               (no HTTP knowledge)
```

- **Routers** handle the HTTP layer: they validate the request (file type, size),
  enforce authentication, and shape the response. They contain no conversion
  logic.
- **Services** contain the actual business logic (document conversion). They know
  nothing about HTTP, which makes them easy to test in isolation and to reuse.
- **Settings** load configuration from environment variables, keeping secrets out
  of the codebase.

This boundary is deliberate: it means the conversion engine can be swapped or
extended (e.g. adding an LLM step) without touching the API layer.

---

## Project Structure

```
document-intelligence-api/
│
├── api/
│   ├── __init__.py
│   ├── main.py               # app entry point, wires routers together
│   ├── settings.py           # environment-based configuration
│   ├── dependencies.py       # shared dependencies (API key auth)
│   ├── schemas.py            # Pydantic request/response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py         # GET /v1/health
│   │   └── documents.py      # POST /v1/documents/convert
│   └── services/
│       ├── __init__.py
│       └── document_service.py   # MarkItDown conversion logic
│
├── tests/
│   └── test_api_documents.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### Requirements

- Python 3.10 or higher (required by MarkItDown)

### Installation

```bash
# Clone the repository
git clone https://github.com/felipenoobrega/document-intelligence-api.git
cd document-intelligence-api

# Create a virtual environment
python -m venv .venv

#Activate the virtual environment
macOS/Linux

source .venv/bin/activate

Windows PowerShell

.venv\Scripts\Activate.ps1


# Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable            | Description                                        | Default |
| ------------------- | -------------------------------------------------- | ------- |
| `APP_API_KEY`       | The key clients must send in the `X-API-Key` header | —       |
| `APP_MAX_FILE_SIZE_MB` | Maximum accepted upload size, in megabytes      | `10`    |

The `.env` file is git-ignored and never committed. `.env.example` documents the
required variables without exposing real values.

---

## Running the API

```bash
uvicorn api.main:app --reload
```

Then open the interactive documentation at:

```
http://127.0.0.1:8000/docs
```

FastAPI generates a full Swagger UI automatically, where you can upload a file
and test the conversion directly in the browser.

---

## API Reference

### `GET /v1/health`

Health check. No authentication required.

**Response**

```json
{
  "status": "ok",
  "service": "document-intelligence-api"
}
```

### `POST /v1/documents/convert`

Converts an uploaded document to Markdown. **Requires** the `X-API-Key` header.

**Request** — `multipart/form-data` with a single `file` field.

**Response**

```json
{
  "file_name": "report.pdf",
  "markdown": "# Report Title\n\nDocument content...",
  "markdown_length": 1234
}
```

**Error responses**

| Status | Meaning                                     |
| ------ | ------------------------------------------- |
| `400`  | Unsupported file type                       |
| `401`  | Missing or invalid API key                  |
| `413`  | File exceeds the configured size limit      |

---

## Scope and Limitations

This project is intentionally scoped. Being explicit about what it does *not* do
is part of using the right tool for the job:

- **Best with digital documents.** PDF text extraction is heuristic. Documents
  generated by software (exported PDFs, Office files) convert cleanly. Scanned
  documents, multi-column academic papers, and PDFs with heavy footnotes are not
  reliably handled and would require an OCR layer (out of scope for V1).
- **Complex tables are lossy.** Spreadsheets with merged cells, formulas, or
  multi-row headers lose information when flattened to Markdown tables.
- **Security by design.** Conversion uses `convert_stream` over the received file
  bytes rather than a generic `convert` that could accept arbitrary URLs, which
  avoids exposing the service to server-side request forgery (SSRF). This follows
  MarkItDown's own guidance to call the narrowest `convert_*` function needed
  (see [References](#references)).

---

## Testing

```bash
pytest
```

The test suite mocks the document service, so tests run in milliseconds without
requiring real files or external calls. Coverage includes:

- Successful conversion returns `200` with the expected Markdown.
- Unsupported file types are rejected with `400`.
- Requests without a valid API key are rejected with `401`.

---

## Roadmap

The current release (V1) is a complete, self-contained document conversion
service with no external AI dependency. Planned extensions:

**V2 — AI layer**

- `POST /v1/documents/summarize` — convert, then summarize via an LLM (Gemini).
- `POST /v1/documents/ask` — convert, then answer questions about the document.
- Token-cost estimation: report how many tokens the raw document would have cost
  versus the converted Markdown, quantifying the savings.
- Structured error handling with custom exceptions (e.g. `DocumentConversionError`,
  `LLMError`).

**V3 — Production hardening**

- Structured field extraction (e.g. invoice number, date, total) with schema-
  constrained output.
- Docker support and `docker-compose` for one-command startup.
- CI/CD pipeline with GitHub Actions (automated tests on every push).
- Document metadata (page count, word count, processing time).

---

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — web framework
- **[MarkItDown](https://github.com/microsoft/markitdown)** — document-to-Markdown
  conversion (Microsoft, MIT licensed)
- **[Pydantic](https://docs.pydantic.dev/)** — data validation and settings
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI server
- **[pytest](https://docs.pytest.org/)** — testing

---

## References

- **MarkItDown — GitHub repository:** <https://github.com/microsoft/markitdown>
- **MarkItDown — PyPI package:** <https://pypi.org/project/markitdown/>
- **MarkItDown — Security Considerations** (rationale for using `convert_stream`):
  <https://github.com/microsoft/markitdown/tree/main/packages/markitdown#security-considerations>
- **FastAPI documentation:** <https://fastapi.tiangolo.com/>
