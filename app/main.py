from fastapi import FastAPI
from app.routers import ingestion, retrieval

app = FastAPI()

# Include routes
app.include_router(ingestion.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(retrieval.router, prefix="/retrieve", tags=["Retrieval"])
