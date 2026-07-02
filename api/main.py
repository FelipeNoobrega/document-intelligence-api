from fastapi import FastAPI

from api.routers import health, documents

app =  FastAPI(title="Document Intelligent API")
app.include_router(health.router)
app.include_router(documents.router)