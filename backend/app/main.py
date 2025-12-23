from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, items, favorites, tags, notes, sources, ingest

app = FastAPI(
    title="MENA Signal API",
    description="AI Funding News & Companies with MENA Applicability Analysis",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "mena-signal-api"}

